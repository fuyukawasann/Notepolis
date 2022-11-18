# importing
from pytube import YouTube
from pytube.cli import on_progress
import ssl


def downYT(url, name):
    ssl._create_default_https_context = ssl._create_unverified_context
    myurl = 'https://www.youtube.com/watch?v=' + url
    yt = YouTube(myurl, on_progress_callback=on_progress)
    # Youtube에서 동영상 다운로드
    stream = yt.streams.get_highest_resolution()
    # 스트리밍 처리
    stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    print(stream)
    print("잠시만 기다리시요...")
    stream.download(filename= name+'.mp4', output_path='./static/')
    print("\n동영상 다운로드 완료!!")