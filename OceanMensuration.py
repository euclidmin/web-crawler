from urllib.parse import urlencode, unquote, quote_plus
import requests
import xml.etree.ElementTree as et


class OceanMensuration:
    def __init__(self):
        pass

    # def make_restfull_query(self):
    def get_mensuration_info(self):
        url = 'http://apis.data.go.kr/1520635/OceanMensurationService/getOceanMesurationDetailcoo'
        data = {
            'ServiceKey': 'B5vTA%2BwSQ0%2FS3w%2BrbawrLgVxGIdztJG1keqskxowzSHEDpWdpFdMHs69UgO4ei3R9aNDcqmjgANp49s%2FVhXiqw%3D%3D',
            'numOfRow': '100'
        }
        encoded_args = urlencode(data, safe='%')
        req_url = url + '?' + encoded_args
        ret = requests.get(req_url)

        return ret


def main():
    om = OceanMensuration()
    mensur_info = om.get_mensuration_info()
    xml_str = mensur_info.content
    xml_s = xml_str.decode('utf8')
    print(xml_s)

    root = et.fromstring(xml_s)

    for item in root.iter('item'):
        mensuration_point = dict()
        mensuration_point['해역'] = item.find('ocean').text
        mensuration_point['관측소코드'] = item.find('staCde').text
        mensuration_point['한글명'] = item.find('staNamKor').text
        mensuration_point['영문명'] = item.find('staNamEng').text
        mensuration_point['위도'] = item.find('lat').text
        mensuration_point['경도'] = item.find('lon').text
        mensuration_point['관측시작일'] = item.find('bldDate').text
        endDate = item.find('endDat')
        mensuration_point['관측종료일'] = endDate.text if endDate else ''

        # print(transaction)
        print(mensuration_point)
        # apt_transactions.append(transaction)



if __name__ == '__main__' :
    main()