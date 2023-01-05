### Notepolis 프로그램을 위한 기본적인 코드 입니다.
import cv2
import os
from PIL import Image
from skimage.metrics import structural_similarity as ssim
from imutils.video import FileVideoStream

import pytesseract
import pdfkit

import time
from time import strftime
from time import gmtime
from datetime import datetime

from PyPDF2 import PdfFileReader, PdfFileWriter

from pytube import YouTube

def notepolis(filename, vidiname, linux=True):
    #OCR config
    pytesseract.pytesseract.tesseract_cmd = R'/usr/bin/tesseract' if linux \
        else R'C:\Program Files\Tesseract-OCR\tesseract'
    config = ('-l eng+kor --oem 3 --psm 4')
    isOnOCR = True #OCR 기능 사용 여부

    #text_PDF config
    conf = pdfkit.configuration(wkhtmltopdf=r"/usr/bin/wkhtmltopdf" if linux \
        else r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')


    ## 1-저장된 영상을 프레임 단위의 사진으로 만든다
    # 1) 동영상의 이름을 받는다
    myName = filename
    videoName = vidiname

    testtime = datetime.now()


    # 2) 동영상을 불러온다
    vfilepath = "./static/" + videoName + ".mp4"
    video = cv2.VideoCapture(vfilepath)

    #output location
    timestamp = str(testtime.timestamp())
    timestamp = timestamp.replace('.','')

    sfilepath = "./static/" + videoName
    try:
        if not os.path.exists(sfilepath):
            os.makedirs(sfilepath)
    except OSError:
        print("에러: 파일 경로를 확인할 수 없습니. " + sfilepath)

    print("파일 경로" + sfilepath)

    if not video.isOpened():
        print("동영상 파일을 열수 없습니다 : ", vfilepath)
        exit(0)

    # 3) 비디오 정보
    length = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = round(video.get(cv2.CAP_PROP_FPS))

    video.release()
    # 2) 디렉토리를 만든다.
    try:
        if not os.path.exists('./outputs'):
            os.makedirs('./outputs')
    except OSError:
            print("output 폴더 생성 실패")

    try:
        if not os.path.exists(sfilepath):
            os.makedirs(sfilepath)
    except OSError:
            print ("에러: 파일 경로를 확인할 수 없습니다. " + sfilepath)
            exit(0)

    # 3) n초당 1프레임 저장
    fvs = FileVideoStream(vfilepath).start()
    #time.sleep(1.0)
    SAMPLING_INTERVAL = 5 #SAMPLIG_INTERVAL초 당 1프레임 저장
    count = 0
    startFrame = 0
    frameA = None
    frameB = None

    #ssim parameter
    THRESHOLD = 0.87

    textlist = []
    imglist_out = []

    while(fvs.more()):
        image = fvs.read()
        #지정 시간 당 프레임 추출
        if((count % (fps*SAMPLING_INTERVAL) == 0)):
            print("프레임 번호 : ", str(count))
            if count == 0:
                startFrame = 0
                frameA = image
            else:
        #프레임 유사도 측정 및 중복 프레임 제거 + OCR 동작
                frameB = image

                grayA = cv2.cvtColor(frameA, cv2.COLOR_BGR2GRAY)
                grayB = cv2.cvtColor(frameB, cv2.COLOR_BGR2GRAY)

                score = ssim(grayA, grayB, full=False)
                print("score : " + str(score))

                if score < THRESHOLD or (count + fps*SAMPLING_INTERVAL) > length:
                    # keyframe 추출시 text 추출 및 pdf화 준비
                    endFrame = count / (fps*SAMPLING_INTERVAL)

                #동영상 시간 기록
                    startTime = strftime("%H:%M:%S", gmtime(startFrame * SAMPLING_INTERVAL))
                    endTime = strftime("%H:%M:%S", gmtime(endFrame * SAMPLING_INTERVAL))
                    text = "start Time  " + str(startTime) \
                           + "\nend Time  " + str(endTime) \
                           + "\n\n\n\n"
                    if isOnOCR:
                        text = text + pytesseract.image_to_string(grayA, config=config) #OCR 동작
                    startFrame = endFrame + 1
                    text = text.replace('\n', '<br>')
                    textlist.append(text)
                    print(textlist)
                    imageA_RGB = cv2.cvtColor(frameA, cv2.COLOR_BGR2RGB)
                    imagePIL = Image.fromarray(imageA_RGB)
                    imglist_out.append(imagePIL)

                frameA = frameB

            if (count + fps*SAMPLING_INTERVAL) > length:
                break

        count += 1

    fvs.stop()


    # 4-남은 프레임을 PDF로 변환한다.
    #이미지 pdf 생성


    cvt_rgb_0 = imglist_out[0]
    cvt_rgb_0.save(sfilepath + '/'+ myName+'img_temp.pdf', save_all = True, append_images=imglist_out[1:])
    f = open(sfilepath + '/'+ myName+'img_temp.pdf', 'rb')
    origin = PdfFileReader(f)
    page_width = origin.pages[0].mediabox.getWidth()
    page_height = origin.pages[0].mediabox.getHeight()

    #텍스트 pdf 생성
    options = {'quiet' : '', 'page-width' : str(page_width/3),
               'page-height' : str(page_height/3), 'minimum-font-size' : str(int(page_height/25)),
               'encoding':"UTF-8"
               }
    writer = PdfFileWriter()
    text_out = ""
    for x in textlist:
        text_out = text_out + x + "<p style=\"page-break-before: always;\"></p>"

    pdfkit.from_string(text_out, sfilepath +'/'+ 'temp.pdf', options=options, configuration=conf)
    g = open(sfilepath +'/'+ 'temp.pdf','rb')
    textpdf = PdfFileReader(g)
    #text pdf, img pdf 교차
    j = 0
    print("imglen : " + str(len(imglist_out)) + "textlen : " + str(len(textlist)))
    for i in range(0,len(textlist)):
        while(i != 0):
            if textpdf.getPage(j).extractText().find("start Time") == -1:
                writer.addPage(textpdf.getPage(j))
                j += 1
            else:
                break
        writer.addPage(origin.getPage(i))
        writer.addPage(textpdf.getPage(j))
        j += 1

    #최종 pdf 저장


    savefilepath = "./static/" + videoName
    try:
        if not os.path.exists(savefilepath):
            os.makedirs(savefilepath)
    except OSError:
        print("에러: 파일 경로를 확인할 수 없습니다. " + savefilepath)


    writer.write(open('./static/' + videoName + '/' + myName + '.pdf', 'wb'))

    f.close()
    g.close()

    #임시 pdf 삭제
    os.remove(sfilepath+'/'+myName+'img_temp.pdf')
    os.remove(sfilepath+'/'+'temp.pdf')

    print("강의 요약 완료")

    #시간 측정
    duration = datetime.now()
    duration = duration - testtime
    print(duration.seconds)


def main():
    print("강의 요약 프로젝트")
    myName = input("저장할 이름 : ")
    videoName = input("동영상 이름 : ")
    notepolis(myName,videoName, False) #window : False , linux : true

if __name__== "__main__":
    main()