import socket
from datetime import datetime
from OpenSSL import SSL
import certifi


def cert_domain_info(hostname, port):
    methods = [
        # (SSL.SSLv2_METHOD, "SSL.SSLv2_METHOD"),
        # (SSL.SSLv3_METHOD, "SSL.SSLv3_METHOD"),
        (SSL.SSLv23_METHOD, "SSL.SSLv23_METHOD"),
        (SSL.TLSv1_METHOD, "SSL.TLSv1_METHOD"),
        (SSL.TLSv1_1_METHOD, "SSL.TLSv1_1_METHOD"),
        (SSL.TLSv1_2_METHOD, "SSL.TLSv1_2_METHOD"),
    ]
    cert_info = {}
    cert_chain = []
    for method, method_name in methods:
        try:
            context = SSL.Context(method=method)
            context.load_verify_locations(cafile=certifi.where())

            conn = SSL.Connection(
                context, socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            )
            conn.settimeout(5)
            conn.connect((hostname, port))
            conn.setblocking(1)
            conn.do_handshake()
            conn.set_tlsext_host_name(hostname.encode())
            for (idx, cert) in enumerate(conn.get_peer_cert_chain()):
                cert_info.update({'Алгоритм шифрования': cert.get_signature_algorithm().decode('utf-8')})
                cert_info.update({'Серийный номер': cert.get_serial_number()})
                cert_info.update({'Хэш имени субъекта': cert.subject_name_hash()})
                lenkey = cert.get_pubkey().bits()
                if lenkey < 512:
                    lenkey *= 8
                cert_info.update({'Длинна открытого ключа': lenkey})
                sub_list = cert.get_subject().get_components()
                issuer = cert.get_issuer().get_components()
                for item in sub_list:
                    if item[0].decode('utf-8') == 'CN':
                        cert_info.update({'Кому выдан': item[1].decode('utf-8')})

                for item in issuer:
                    if item[0].decode('utf-8') == 'CN':
                        cert_info.update({'Кем выдан': item[1].decode('utf-8')})
                cert_info.update({'Действует до': str(datetime.strptime(str(cert.get_notAfter().decode('utf-8')),
                                                                        "%Y%m%d%H%M%SZ"))})
                cert_chain.append(cert_info.copy())
            conn.close()
        except:
            continue
    for i in cert_chain:
        if cert_chain.count(i) > 1:
            cert_chain.remove(i)
    return cert_chain


def is_valid_period_exceeded(cert_chain):
    if len(cert_chain) < 1:
        return "Сертификат не найден"
    for i in cert_chain:
        if not 'Действует до' in i:
            return str("Сертификат с серийным номером: " + str(i['Серийный номер']) + ", выданный компании: " + str(
                i['Кому выдан']) + "просрочен. Безопасное соединение не гарантируется!")
    return str("Срок действия всех сертификатов в цепочке подтвержден")


def is_certified_by_trusted_root_certification_authority(list_of_trca, cert_chain):
    if len(cert_chain) < 1:
        return "Сертификат не найден"
    if cert_chain[-1]["Кем выдан"] in list_of_trca:
        return str("Сертификационная цепочка валидна")
    if cert_chain[-1]["Кем выдан"] == 'invalid2.invalid':
        return str("Сертификат домена не содержит данные о эмитенте. Возможно сертификат домена является "
                   "самоподписанным. Безопасное соединение не гарантируется!")
    return str(
        "В сертификационной цепочке не обнаружен доверенный корневой центр сертификации: сертификат домена является "
        "самоподписанным. Безопасное соединение не гарантируется!")


def is_valid_period_too_long(cert_chain):
    if len(cert_chain) < 1:
        return "Сертификат не найден"
    l = cert_chain[0]['Действует до']
    val_per = list(map(int, l.split(" ")[0].split("-"))) + list(map(int, l.split(" ")[1].split(":")))
    t = datetime(year=val_per[0], month=val_per[1], day=val_per[2], hour=val_per[3], minute=val_per[4],
                 second=val_per[5])
    if int(str(t - datetime.now().replace(microsecond=0)).split(" ")[0]) > 366:
        return str("Сертификат выдан более чем на 1 год: " + str(
            int(str(t - datetime.now().replace(microsecond=0)).split(" ")[0])) + " дней")
    return "Срок действия сертификата не привышает 1 года"


def is_public_key_length_enough(cert_chain):
    if len(cert_chain) < 1:
        return "Сертификат не найден"
    if cert_chain[0]['Длинна открытого ключа'] < 2048:
        return "Длинна ключа слишком мала"
    return "Длинна ключа соответсвует требованиям"


def is_certificate_issued_by_specific_CA(name_ca, cert_chain):
    if len(cert_chain) < 1:
        return "Сертификат не найден"
    if name_ca == cert_chain[-1]['Кем выдан']:
        return "Сертификат для данного домена был выдан удостоверяющим центром " + name_ca
    else:
        for i in cert_chain:
            if name_ca == i['Кем выдан']:
                return "В цепочке сертификации для данного домена присутствует удостоверяющий центр " + name_ca
    return "Указанный удостоверяющий центр не присутствует в цепочке сертификации"


def is_valid_period_ends_before_specified_date(date, cert_chain):
    if len(cert_chain) < 1:
        return "Сертификат не найден"
    l = cert_chain[0]['Действует до']
    val_per = list(map(int, l.split(" ")[0].split("-"))) + list(map(int, l.split(" ")[1].split(":")))
    t = datetime(year=val_per[0], month=val_per[1], day=val_per[2], hour=val_per[3], minute=val_per[4],
                 second=val_per[5])
    if int(str(t - date).split(" ")[0]) < 0:
        return "Период действия сертификата истекает до указанной даты"
    return "Период действия сертификата истекает после указанной даты"


def is_encription_algorithm_unreliable(cert_chain):
    for i in cert_chain:
        if "sha256WithRSAEncryption" != i['Алгоритм шифрования'] or "ecdsa-with-SHA384" != i[
            'Алгоритм шифрования'] or "ecdsa-with-SHA256" != i['Алгоритм шифрования']:
            return "В цепочке сертификации присутствует ненадежный алгоритм шифрования"
    return "Все алгоритмы шифрования в цепочке надежны"
