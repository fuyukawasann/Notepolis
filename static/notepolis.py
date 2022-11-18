### Notepolis 프로그램을 위한 기본적인 코드 입니다.
import cv2
import os
from PIL import Image
from skimage.metrics import structural_similarity as ssim
from datetime import datetime
import imutils
from skimage import io
import argparse
import shutil


def notepolis(filename, vidiname):
    # 1-저장된 영상을 프레임 단위의 사진으로 만든다
    # 1) 저장할 이름을 받는다.
    myName = filename
    videoName = vidiname
    # 2) 프레임 정보를 가져온다.
    vfilepath = "./static/" + videoName + ".mp4"
    video = cv2.VideoCapture(vfilepath)

    if not video.isOpened():
        print("동영상 파일을 열수 없습니다 : ", vfilepath)
        exit(0)
    # 3) 비디오 정보
    length = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = round(video.get(cv2.CAP_PROP_FPS))
    # 2) 디렉토리를 만든다.
    sfilepath = "./static/" + videoName
    try:
        if not os.path.exists(sfilepath):
            os.makedirs(sfilepath)
    except OSError:
        print("에러: 파일 경로를 확인할 수 없습니. " + sfilepath)
    # 3) 1초당 1프레임 저장
    count = 0

    while (video.isOpened()):
        ret, image = video.read()
        if (int(video.get(1)) % fps == 0):
            cv2.imwrite(sfilepath + "/frame%d.jpg" % count, image)
            print("프레임 저장 번호 : ", str(int(video.get(1))))
            count += 1
        if int(video.get(1)) == length:
            break

    video.release()

    # 2-동영상을 제거한다.
    os.remove(vfilepath)
    print("동영상 제거!!")


    # 3-프래임에서 필요한 정보만을 남긴다.
    print("중복된 사진 제거")
    # 1) parse를 찍는다
    ap = argparse.ArgumentParser()
    filenum = len(os.listdir(sfilepath))
    # 2) 사진 비교 및 유사도 일정 수치 이상시 제거
    for i in range(filenum - 1):
        First = sfilepath + "/frame" + str(i) + ".jpg"
        Second = sfilepath + "/frame" + str(i + 1) + ".jpg"

        args = vars(ap.parse_args())
        # 이미지 로드
        imageA = cv2.imread(First)
        imageB = cv2.imread(Second)
        # 그레이 코드
        grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
        grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)
        # 스코어 저장
        (score, diff) = ssim(grayA, grayB, full=True)
        diff = (diff * 255).astype("uint8")
        # 스코어(유사도)가 0.87 이상이면 첫 번째 사진 제
        if score >= 0.87:
            os.remove(First)

    # 4-남은 프레임을 PDF로 변환한다.
    print("PDF로 변환")
    file_list = os.listdir(sfilepath)

    img_list = []
    img_path = sfilepath + "/" + file_list[0]
    im_buf = Image.open(img_path)
    cvt_rgb_0 = im_buf.convert('RGB')
    for i in file_list:
        img_path = sfilepath + "/" + i
        im_buf = Image.open(img_path)
        cvt_rgb = im_buf.convert('RGB')
        img_list.append(cvt_rgb)

    del img_list[0]
    savefilepath = "./static/" + videoName
    try:
        if not os.path.exists(savefilepath):
            os.makedirs(savefilepath)
    except OSError:
        print("에러: 파일 경로를 확인할 수 없습니다. " + savefilepath)
    cvt_rgb_0.save('./static/' + videoName + '/' + myName + '.pdf', save_all=True, append_images=img_list)

    # 5-사진 파일 마저 지운다.
    # shutil.rmtree(sfilepath, ignore_errors=True)
    # print("사진 제거")
    print("강의 요약 완료")