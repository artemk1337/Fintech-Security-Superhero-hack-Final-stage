# !pip install cryptography

import requests
from PIL import Image
from jwt_rsa.token import JWT
from jwt_rsa.rsa import generate_rsa
import json
import ctypes


Headers = None


Bits = 2048
PrivateKey, PublicKey = generate_rsa(Bits)
jwt = JWT(PrivateKey, PublicKey)


def validate_person(image):
    def block_system():
        ctypes.windll.user32.LockWorkStation()
        # os.kill(os.getpid(), signal.SIGINT)
        pass

    url = 'https://f2a.akbars.digital/hack/api/Validator/validate'
    payload = {'ProjectId': 'Hackathon',
               'isCropped': 'false',
               'Clientid': '0E4E0009-7475-4C72-8D82-C25B66A59384',
               'Modelid': '1'}
    files = [('image', image)]

    try:
        response = requests.request("POST", url, headers=Headers, data=payload, files=files)
    # no internet connection
    except requests.ConnectionError:
        # save logs
        block_system()
        quit(-1)

    response = json.loads(response.text)
    # print(response['result'].encode('UTF-8'))
    jwt_decoded = jwt.decode(response['result'], verify=False)\
        if 'result' in response else None
    # print(response)
    if response['success'] is False:
        if response['errorCode'] == 'NotFound':
            # print('Пользователь не найден')
            # action
            return 1, 'Пользователь не найден'
        elif response['errorCode'] == 'FailedToFindFace':
            # print('На удалось найти лицо на фото')
            # action
            return 2, 'На удалось найти лицо'
        elif response['errorCode'] == 'InvalidData':
            # print('Неправильно заполнено одно из полей')
            # action
            return 3, 'Неправильно заполнено одно из полей'
        return 0, response['errorCode']
    return response, jwt_decoded


def add_new_person(image):
    url = 'https://f2a.akbars.digital/hack/api/Validator/RegisterNewCustomer'
    payload = {'ProjectId': 'Hackathon',
               'ClientId': '0E4E0009-7475-4C72-8D82-C25B66A59384',
               'isCropped': 'false'}
    files = [('image', image)]
    response = requests.request("POST", url, headers=Headers, data=payload, files=files)
    response = json.loads(response.text)
    jwt_decoded = jwt.decode(response['result']['customerToken'], verify=False) \
        if 'result' in response else None
    if response['success'] is False:
        if response['errorCode'] == 'AlreadyExist':
            print('Пользователь уже существует')
            # action
            return 1, 'Пользователь уже существует'
        elif response['errorCode'] == 'FailedToFindFace':
            print('На удалось найти лицо')
            # action
            return 2, 'На удалось найти лицо'
        elif response['errorCode'] == 'InvalidData':
            print('Неправильно заполнено одно из полей')
            # action
            return 3, 'Неправильно заполнено одно из полей'
        return 0, response['errorCode']
    return response, jwt_decoded


def add_photo_person(image):
    url = 'https://f2a.akbars.digital/hack/api/Validator/AddVectorsForCustomerWithId'
    payload = {'ProjectId': 'Hackathon',
               'ClientId': '0E4E0009-7475-4C72-8D82-C25B66A59384',
               'isCropped': 'false',
               'CustomerId': 'f4827468-e051-4291-86ba-229901a2aae5'}
    files = [('image', image)]
    response = requests.request("POST", url, headers=Headers, data=payload, files=files)
    response = json.loads(response.text)
    jwt_decoded = jwt.decode(response['result']['customerToken'], verify=False) \
        if 'result' in response else None
    if response['success'] is False:
        if response['errorCode'] == 'Missmatch':
            print('Фото лиц не совпадают')
            # action
            return 1, 'Фото лиц не совпадают'
        elif response['errorCode'] == 'FailedToFindFace':
            print('На удалось найти лицо')
            # action
            return 2, 'На удалось найти лицо'
        elif response['errorCode'] == 'InvalidData':
            print('Неправильно заполнено одно из полей')
            # action
            return 3, 'Неправильно заполнено одно из полей'
        return 0, response['errorCode']
    return response, jwt_decoded


def del_person(id_):
    url = 'https://f2a.akbars.digital/hack/api/Face2Action/RemoveCustomer'
    payload = str({"Id": id_})
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", url, headers=headers, data=payload)
    response = json.loads(response.text)
    if response['success'] is False:
        return 0, response['errorCode']
    return response


def get_customerId(info):
    return info['customerId']


if __name__ == "__main__":
    # add_info = add_new_person(open('E:/Python_programs/work/files/faces.jpg', 'rb'))
    # print(add_info)

    # add_photo_info = add_photo_person(open('E:/Python_programs/work/files/face.jpg', 'rb'))
    # print(add_photo_info)

    # validate_info = validate_person(open('E:/Python_programs/work/files/faces.jpg', 'rb'))
    # print(validate_info)

    # del_info = del_person('64e4d4b1-5cbe-4863-a653-9cf54a1a7e0b')
    # print(del_info)

    pass
