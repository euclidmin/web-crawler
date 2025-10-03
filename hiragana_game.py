import json
import os
import random
import threading
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import tkinter as tk
from tkinter import messagebox


try:
    from gtts import gTTS  # type: ignore
    from playsound import playsound  # type: ignore

    TTS_AVAILABLE = True
except Exception as exc:  # pragma: no cover - defensive import guard
    print("[안내] gTTS 또는 playsound 라이브러리를 불러올 수 없어 음성 기능이 비활성화됩니다.")
    print(f"[안내] 상세 오류: {exc}")
    TTS_AVAILABLE = False


STATS_FILE = "hiragana_stats.json"
INITIAL_POOL_SIZE = 10
NEW_CHARS_ON_LEVEL_UP = 10
LEVEL_UP_THRESHOLD = 0.8
CONSECUTIVE_ANSWERS_FOR_MEMORIZED = 5
QUICK_REVIEW_CONSECUTIVE_ANSWERS = 3


class TTSManager:
    """gTTS와 playsound를 활용한 간단한 음성 재생 관리 클래스."""

    def __init__(self) -> None:
        self.enabled = TTS_AVAILABLE

    def play(self, text: str, lang: str, delay: float = 0.0) -> None:
        if not self.enabled:
            return

        def _worker() -> None:
            try:
                if delay:
                    time.sleep(delay)
                tts = gTTS(text=text, lang=lang)
                temp_file = f"temp_audio_{int(time.time() * 1000)}_{threading.get_ident()}.mp3"
                tts.save(temp_file)
                try:
                    playsound(temp_file)
                finally:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
            except Exception as error:  # pragma: no cover - 방어적 로그
                print(f"[오류] 음성 재생 중 문제가 발생했습니다: {error}")

        threading.Thread(target=_worker, daemon=True).start()


class HiraganaData:
    """히라가나와 로마자 데이터 집합."""

    def __init__(self) -> None:
        self.hiragana_pairs: List[Tuple[str, str]] = [
            ("あ", "a"), ("い", "i"), ("う", "u"), ("え", "e"), ("お", "o"),
            ("か", "ka"), ("き", "ki"), ("く", "ku"), ("け", "ke"), ("こ", "ko"),
            ("さ", "sa"), ("し", "shi"), ("す", "su"), ("せ", "se"), ("そ", "so"),
            ("た", "ta"), ("ち", "chi"), ("つ", "tsu"), ("て", "te"), ("と", "to"),
            ("な", "na"), ("に", "ni"), ("ぬ", "nu"), ("ね", "ne"), ("の", "no"),
            ("は", "ha"), ("ひ", "hi"), ("ふ", "fu"), ("へ", "he"), ("ほ", "ho"),
            ("ま", "ma"), ("み", "mi"), ("む", "mu"), ("め", "me"), ("も", "mo"),
            ("や", "ya"), ("ゆ", "yu"), ("よ", "yo"),
            ("ら", "ra"), ("り", "ri"), ("る", "ru"), ("れ", "re"), ("ろ", "ro"),
            ("わ", "wa"), ("を", "wo"), ("ん", "n"),
        ]

        if len(self.hiragana_pairs) != 46:
            raise ValueError("히라가나 데이터가 46개가 아닙니다.")

        self.hiragana_to_romaji: Dict[str, str] = dict(self.hiragana_pairs)
        self.ALL_ROMAJI_OPTIONS: List[str] = sorted({romaji for _, romaji in self.hiragana_pairs})


def default_hiragana_status() -> Dict[str, Dict[str, List[bool]]]:
    return {char: {"recent_answers": []} for char, _ in HiraganaData().hiragana_pairs}


@dataclass
class LearningStatistics:
    total_questions: int = 0
    correct_answers_count: int = 0
    current_pool_size: int = INITIAL_POOL_SIZE
    hiragana_status: Dict[str, Dict[str, List[bool]]] = field(default_factory=default_hiragana_status)

    @classmethod
    def load(cls) -> "LearningStatistics":
        if not os.path.exists(STATS_FILE):
            return cls()
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as fp:
                raw = json.load(fp)
            stats = cls()
            stats.total_questions = int(raw.get("total_questions", 0))
            stats.correct_answers_count = int(raw.get("correct_answers_count", 0))
            stats.current_pool_size = int(raw.get("current_pool_size", INITIAL_POOL_SIZE))
            status = raw.get("hiragana_status", {})
            if not isinstance(status, dict):
                raise ValueError("잘못된 상태 데이터")
            template = default_hiragana_status()
            for char, data in template.items():
                answers = status.get(char, {}).get("recent_answers", [])
                if isinstance(answers, list) and all(isinstance(x, bool) for x in answers):
                    # 최근 정답 기록은 True 값만 저장한다.
                    data["recent_answers"] = [True for x in answers if x]
                else:
                    data["recent_answers"] = []
            stats.hiragana_status = template
            return stats
        except Exception:
            return cls()

    def save(self) -> None:
        payload = {
            "total_questions": self.total_questions,
            "correct_answers_count": self.correct_answers_count,
            "current_pool_size": self.current_pool_size,
            "hiragana_status": self.hiragana_status,
        }
        with open(STATS_FILE, "w", encoding="utf-8") as fp:
            json.dump(payload, fp, ensure_ascii=False, indent=2)

    def reset(self) -> None:
        self.total_questions = 0
        self.correct_answers_count = 0
        self.current_pool_size = INITIAL_POOL_SIZE
        self.hiragana_status = default_hiragana_status()

    def register_answer(self, char: str, correct: bool, max_consecutive: int) -> None:
        self.total_questions += 1
        entry = self.hiragana_status.setdefault(char, {"recent_answers": []})
        if correct:
            self.correct_answers_count += 1
            entry["recent_answers"].append(True)
            if len(entry["recent_answers"]) > max_consecutive:
                entry["recent_answers"] = entry["recent_answers"][-max_consecutive:]
        else:
            entry["recent_answers"].clear()

    def consecutive_correct(self, char: str) -> int:
        entry = self.hiragana_status.get(char, {"recent_answers": []})
        return len(entry.get("recent_answers", []))

    def memorized_count(self, pool_chars: List[str], threshold: int) -> int:
        return sum(1 for char in pool_chars if self.consecutive_correct(char) >= threshold)


class QuizManager:
    def __init__(self, data: HiraganaData, stats: LearningStatistics) -> None:
        self.data = data
        self.stats = stats
        self.previous_char: Optional[str] = None
        self.asked_tracker: Dict[str, int] = {char: 0 for char, _ in self.data.hiragana_pairs}
        self.override_pool_size: Optional[int] = None

    def get_current_pool(self) -> List[str]:
        size = self.override_pool_size
        if size is None:
            size = self.stats.current_pool_size
        size = min(size, len(self.data.hiragana_pairs))
        return [char for char, _ in self.data.hiragana_pairs[:size]]

    def _available_chars(self, threshold: int) -> List[str]:
        pool = self.get_current_pool()
        candidates = [
            char for char in pool if self.stats.consecutive_correct(char) < threshold
        ]
        if not candidates:
            return pool
        return candidates

    def pick_question(self, threshold: int) -> str:
        candidates = self._available_chars(threshold)
        if len(candidates) > 1 and self.previous_char in candidates:
            candidates = [char for char in candidates if char != self.previous_char]
            if not candidates:
                candidates = self._available_chars(threshold)

        weights = []
        for char in candidates:
            asked = self.asked_tracker.get(char, 0)
            if asked == 0:
                weight = 20
            else:
                streak = self.stats.consecutive_correct(char)
                weight = max(1, 20 - (streak * 4))
            weights.append(weight)

        chosen = random.choices(candidates, weights=weights, k=1)[0]
        self.previous_char = chosen
        self.asked_tracker[chosen] = self.asked_tracker.get(chosen, 0) + 1
        return chosen

    def build_options(self, answer_char: str) -> List[str]:
        correct = self.data.hiragana_to_romaji[answer_char]
        options = {correct}
        while len(options) < 5:
            options.add(random.choice(self.data.ALL_ROMAJI_OPTIONS))
        option_list = list(options)
        random.shuffle(option_list)
        return option_list


class HiraganaGameApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("히라가나 암기 게임 (지능형 학습)")
        self.root.geometry("950x750")

        self.data = HiraganaData()
        self.stats = LearningStatistics.load()
        self.quiz_manager = QuizManager(self.data, self.stats)
        self.tts = TTSManager()

        self.mode = "general"  # "general" or "quick"
        self.current_char: Optional[str] = None
        self.correct_romaji: Optional[str] = None
        self.buttons: List[tk.Button] = []
        self.dashboard_labels: Dict[str, tk.Label] = {}
        self.hiragana_labels: Dict[str, tk.Label] = {}

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)

        self.start_general_mode(initial=True)

    # ------------------------------------------------------------------
    # UI 구축
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.game_panel = tk.Frame(self.main_frame, width=600, padx=30, pady=30)
        self.game_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.dashboard_panel = tk.Frame(self.main_frame, width=350, padx=20, pady=20, bg="#f2f2f2")
        self.dashboard_panel.pack(side=tk.RIGHT, fill=tk.BOTH)

        self.question_label = tk.Label(
            self.game_panel,
            text="",
            font=("Helvetica", 150),
            pady=40,
        )
        self.question_label.pack()

        self.feedback_label = tk.Label(self.game_panel, text="", font=("Helvetica", 20))
        self.feedback_label.pack(pady=10)

        self.options_frame = tk.Frame(self.game_panel)
        self.options_frame.pack(fill=tk.Y, expand=True)

        for _ in range(5):
            btn = tk.Button(
                self.options_frame,
                text="",
                font=("Helvetica", 18),
                width=20,
                command=lambda option_index=_: None,
            )
            self.buttons.append(btn)
        for index, btn in enumerate(self.buttons):
            btn.configure(command=lambda idx=index: self.on_option_selected(idx))
            btn.pack(pady=5)

        # 대시보드 패널
        title = tk.Label(
            self.dashboard_panel,
            text="실시간 학습 현황",
            font=("Helvetica", 20, "bold"),
            bg="#f2f2f2",
        )
        title.pack(anchor="w")

        self.stats_frame = tk.Frame(self.dashboard_panel, bg="#f2f2f2")
        self.stats_frame.pack(anchor="w", pady=15)

        self.dashboard_labels["total_questions"] = tk.Label(
            self.stats_frame, text="총 문제 수: 0", font=("Helvetica", 14), bg="#f2f2f2"
        )
        self.dashboard_labels["total_questions"].pack(anchor="w")

        self.dashboard_labels["accuracy"] = tk.Label(
            self.stats_frame, text="정답률: 0%", font=("Helvetica", 14), bg="#f2f2f2"
        )
        self.dashboard_labels["accuracy"].pack(anchor="w")

        self.dashboard_labels["memorized"] = tk.Label(
            self.stats_frame,
            text="현재 학습 범위 내 암기 현황: 0 / 0",
            font=("Helvetica", 14),
            bg="#f2f2f2",
        )
        self.dashboard_labels["memorized"].pack(anchor="w")

        self.dashboard_labels["pool_size"] = tk.Label(
            self.stats_frame,
            text="현재 학습 범위 크기: 0",
            font=("Helvetica", 14),
            bg="#f2f2f2",
        )
        self.dashboard_labels["pool_size"].pack(anchor="w")

        grid_frame = tk.Frame(self.dashboard_panel, bg="#f2f2f2")
        grid_frame.pack(pady=10)

        columns = 8
        for idx, (char, _) in enumerate(self.data.hiragana_pairs):
            lbl = tk.Label(
                grid_frame,
                text=char,
                font=("Helvetica", 18),
                width=3,
                relief=tk.FLAT,
                bg="#cccccc",
            )
            row = idx // columns
            col = idx % columns
            lbl.grid(row=row, column=col, padx=4, pady=4)
            self.hiragana_labels[char] = lbl

        control_frame = tk.Frame(self.dashboard_panel, bg="#f2f2f2")
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)

        self.exit_button = tk.Button(control_frame, text="끝내기", command=self.on_exit, font=("Helvetica", 14))
        self.exit_button.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

        self.reset_button = tk.Button(
            control_frame, text="통계 초기화", command=self.on_reset_statistics, font=("Helvetica", 14)
        )
        self.reset_button.pack(side=tk.RIGHT, padx=5, expand=True, fill=tk.X)

        self.completion_frame = tk.Frame(self.root, padx=40, pady=40)

        self.completion_message = tk.Label(
            self.completion_frame,
            text="학습 완료! 축하합니다!",
            font=("Helvetica", 32, "bold"),
        )
        self.completion_message.pack(pady=20)

        tk.Button(
            self.completion_frame,
            text="통계 초기화 후 다시 시작",
            font=("Helvetica", 18),
            command=self.on_reset_statistics,
            width=25,
        ).pack(pady=10)

        tk.Button(
            self.completion_frame,
            text="빠른 복습 모드",
            font=("Helvetica", 18),
            command=self.start_quick_review_mode,
            width=25,
        ).pack(pady=10)

        tk.Button(
            self.completion_frame,
            text="게임 종료",
            font=("Helvetica", 18),
            command=self.on_exit,
            width=25,
        ).pack(pady=10)

    # ------------------------------------------------------------------
    # 모드 제어 및 초기화
    # ------------------------------------------------------------------
    def start_general_mode(self, initial: bool = False) -> None:
        self.mode = "general"
        if initial and self.stats.current_pool_size < INITIAL_POOL_SIZE:
            self.stats.current_pool_size = INITIAL_POOL_SIZE
        else:
            self.stats.current_pool_size = max(self.stats.current_pool_size, INITIAL_POOL_SIZE)
        self.quiz_manager.override_pool_size = None
        self.show_game_panel()
        self.next_question()

    def start_quick_review_mode(self) -> None:
        self.mode = "quick"
        self.quiz_manager.override_pool_size = len(self.data.hiragana_pairs)
        self.show_game_panel()
        self.next_question()

    def show_game_panel(self) -> None:
        self.completion_frame.pack_forget()
        self.main_frame.pack(fill=tk.BOTH, expand=True)

    def show_completion_panel(self) -> None:
        self.main_frame.pack_forget()
        self.completion_frame.pack(fill=tk.BOTH, expand=True)

    # ------------------------------------------------------------------
    # 문제 출제 및 처리
    # ------------------------------------------------------------------
    def current_threshold(self) -> int:
        return CONSECUTIVE_ANSWERS_FOR_MEMORIZED if self.mode == "general" else QUICK_REVIEW_CONSECUTIVE_ANSWERS

    def next_question(self) -> None:
        threshold = self.current_threshold()
        pool = self.quiz_manager.get_current_pool()
        memorized = self.stats.memorized_count(pool, threshold)
        if pool and memorized >= len(pool):
            self.show_completion_panel()
            self.update_dashboard()
            return

        char = self.quiz_manager.pick_question(threshold)
        self.current_char = char
        self.correct_romaji = self.data.hiragana_to_romaji[char]
        self.question_label.configure(text=char, fg="black")
        self.feedback_label.configure(text="")
        options = self.quiz_manager.build_options(char)
        for btn, option in zip(self.buttons, options):
            btn.configure(text=option, state=tk.NORMAL)
        self.tts.play(char, lang="ja")
        self.update_dashboard()

    def on_option_selected(self, index: int) -> None:
        if self.current_char is None or self.correct_romaji is None:
            return
        selected = self.buttons[index].cget("text")
        for btn in self.buttons:
            btn.configure(state=tk.DISABLED)

        self.tts.play(selected, lang="en")

        is_correct = selected == self.correct_romaji
        self.stats.register_answer(self.current_char, is_correct, CONSECUTIVE_ANSWERS_FOR_MEMORIZED)
        self.update_dashboard()

        if is_correct:
            self.feedback_label.configure(text="정답!", fg="green")
            self.root.after(1000, self.handle_post_answer)
        else:
            self.feedback_label.configure(text="오답!", fg="red")
            self.question_label.configure(text=f"{self.current_char}\n{self.correct_romaji}", fg="blue")
            self.tts.play(self.correct_romaji, lang="en", delay=0.5)
            self.root.after(3000, self.handle_post_answer)

    def handle_post_answer(self) -> None:
        if self.mode == "general":
            self.check_for_level_up()
        self.next_question()

    # ------------------------------------------------------------------
    # 레벨업 및 통계 처리
    # ------------------------------------------------------------------
    def check_for_level_up(self) -> None:
        pool = self.quiz_manager.get_current_pool()
        threshold = self.current_threshold()
        memorized = self.stats.memorized_count(pool, threshold)
        if not pool:
            return
        ratio = memorized / len(pool)
        if ratio >= LEVEL_UP_THRESHOLD and len(pool) < len(self.data.hiragana_pairs):
            new_size = min(len(self.data.hiragana_pairs), len(pool) + NEW_CHARS_ON_LEVEL_UP)
            self.stats.current_pool_size = new_size

    # ------------------------------------------------------------------
    # 대시보드 갱신
    # ------------------------------------------------------------------
    def update_dashboard(self) -> None:
        total = self.stats.total_questions
        correct = self.stats.correct_answers_count
        accuracy_value = 0.0 if total == 0 else round((correct / total) * 100, 1)
        accuracy_text = int(accuracy_value) if accuracy_value.is_integer() else accuracy_value
        pool = self.quiz_manager.get_current_pool()
        threshold = self.current_threshold()
        memorized = self.stats.memorized_count(pool, threshold)

        self.dashboard_labels["total_questions"].configure(text=f"총 문제 수: {total}")
        self.dashboard_labels["accuracy"].configure(text=f"정답률: {accuracy_text}%")
        self.dashboard_labels["memorized"].configure(
            text=f"현재 학습 범위 내 암기 현황: {memorized} / {len(pool)}"
        )
        self.dashboard_labels["pool_size"].configure(
            text=f"현재 학습 범위 크기: {len(pool)}"
        )

        pool_set = set(pool)
        for char, label in self.hiragana_labels.items():
            streak = self.stats.consecutive_correct(char)
            if char not in pool_set:
                label.configure(bg="#cccccc", fg="black")
            elif streak >= threshold:
                label.configure(bg="#3366ff", fg="white")
            elif streak > 0:
                label.configure(bg="#ff6666", fg="white")
            else:
                label.configure(bg="#ff9999", fg="black")

    # ------------------------------------------------------------------
    # 통계 초기화 및 종료 처리
    # ------------------------------------------------------------------
    def on_reset_statistics(self) -> None:
        if not messagebox.askyesno("확인", "정말로 모든 학습 기록을 초기화하시겠습니까?"):
            return
        if os.path.exists(STATS_FILE):
            try:
                os.remove(STATS_FILE)
            except OSError:
                pass
        self.stats.reset()
        self.quiz_manager = QuizManager(self.data, self.stats)
        self.mode = "general"
        self.start_general_mode(initial=True)

    def on_exit(self) -> None:
        try:
            self.stats.save()
        finally:
            self.root.destroy()


def main() -> None:
    root = tk.Tk()
    app = HiraganaGameApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

