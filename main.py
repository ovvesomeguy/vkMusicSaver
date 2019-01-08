import vk_api # импортирование библиотеки в проект
from vk_api.longpoll import VkLongPoll , VkEventType
import requests
import bs4
import json

MUSIC_URL = 'https://vrit.me'
KEY = 'f6c84ce096a30819e5146dc8757a4cdbdc5b82531d5509d41b5fa5e9cad5acd355ee87b058af1e17d6fcb' 
vk = vk_api.VkApi(token=KEY) # собственно сама авторизация


def check(): # функция возращающая  последнее пришедшее сообщение и ID пользователя который его отправил
    answer = {}
    longpoll = VkLongPoll(vk)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.from_user:
                answer['id'] = event.user_id
                answer['message'] = event.text
                return answer


def musicGet(id): # функция будет принимать только id пользователя
    siteUrl = requests.get(MUSIC_URL + '/audios{0}'.format(id)) # открытие сайта 
    htmlMusicContent = bs4.BeautifulSoup(siteUrl.text , 'html.parser')
    allLinks = htmlMusicContent.find_all('a') # выбор всех ссылок
    allTitles = htmlMusicContent.find_all('div' , attrs={'class':'title'}) # выбор всех названий песен
    reallyLinks = allLinks[7:-1] # отсев настоящих ссылок
    i = 0
    answer = []
    while  i < len(reallyLinks):
        value = {'title': allTitles[i+1].getText(), 'link':MUSIC_URL + reallyLinks[i]['href']}
        answer.append(value)
        i += 1
    # создание ответа
    return answer

def uploadDoc(user_id):
    document = vk.method('docs.getMessagesUploadServer' , {'peer_id': user_id})
    upload = requests.post(document['upload_url'] , files = {'file':open('file.txt','rb')})
    result = json.loads(upload.text)
    file = result['file']
    document = vk.method('docs.save' , {'file':file, 'title':'Документ'})[0]
    theAnswer = {'owner_id':document['owner_id'] , 'id':document['id']}
    return theAnswer

def writeFile(text):
    with open('file.txt' , 'w') as file:
        for c in text:
            file.write(c['title'] + ' ' + c['link'] + '\n\n')

if __name__ == '__main__':
    while True:
        serverUp = check()
        x = uploadDoc( serverUp['id'])
        if serverUp.get('message') == 'музыка':
            message = musicGet(serverUp['id']) # эта строка пока может быть вам не понятна, ничего страшного
            writeFile(message)
            attach = 'doc'+str(x['owner_id'])+'_'+str(x['id'])
            vk.method('messages.send' , {'user_id':serverUp['id'] , 'message':'Вот держи' , 'attachment':attach})


