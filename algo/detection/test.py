
# -*-coding:UTF-8
import os
import torch_learn
from task_videocapture import cVideoFrameCapture
import cv2
from algoscope.person_detection.person_detection_main import cPersonDetection
import subprocess as sp

def main():
    rtsp_url = 'rtsp://admin:spaceqwer1234@192.168.1.105:554/Streaming/Channels/202'

    model = cPersonDetection()
    model.add_sub_processor(0)

    # 捕获视频流
    vcap = cVideoFrameCapture(rtsp_url)
    vcap.start_capture()

    # 推送视频流
    rtmp_url = "rtmp://joy.space.top:1935/live/room"
    command = [
        "/usr/local/bin/ffmpeg",
        '-y',  # 覆盖输出文件
        '-f', 'rawvideo',  # 输入格式
        '-pix_fmt', 'bgr24',  # 像素格式
        '-s', '640x360',  # 视频分辨率（需要和输出分辨率一致）
        '-r', '25',  # 帧率
        '-i', '-',  # 从标准输入读取数据
        '-c:v', 'libx264',  # 编码器
        '-preset', 'veryfast',  # 编码速度
        '-f', 'flv',  # 输出格式
        rtmp_url  # RTMP服务器地址
    ]
    print(1)
    pipe = sp.Popen(command, stdin=sp.PIPE) # 创建FFmpeg子进程
    print(2)
    while (vcap.started):
        print(3)
        input_image, timestamp_ms = vcap.fetch_one_frame()
        print(timestamp_ms, input_image.shape)
        camid_cvimg_dict = {0: input_image}
        # camID_results = model.process(camid_cvimg_dict, timestamp_ms)
        # if len(camID_results) > 0:
        #     output_image = camID_results[0]
        #     cv2.imshow('frame', output_image)

            # 将视频帧通过管道发送给FFmpeg
            # pipe.stdin.write(output_image.tobytes())
        pipe.stdin.write(input_image.tobytes())

        # if cv2.waitKey(1) == 27:
        #     break

    vcap.stop_capture()

    pipe.stdin.close()
    pipe.wait()

if __name__ == "__main__":
    main()
