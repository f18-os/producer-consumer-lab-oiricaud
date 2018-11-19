#!/usr/bin/env python3

import threading
import time
import logging
import queue
import cv2
import os

# globals
outputDir = 'frames'
clipFileName = 'clip.mp4'
frameDelay   = 42       # the answer to everything
startTime = time.time()

# filename of clip to load
filename = 'clip2.mp4'

# open the video clip
vidcap = cv2.VideoCapture(clipFileName)
extractionQueue = queue.Queue()

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s', )

BUF_SIZE = 10
q = queue.Queue(BUF_SIZE)



class ProducerThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super(ProducerThread, self).__init__()
        self.target = target
        self.name = name

    def run(self):
        while True:
            if not q.full():
                extract_color_frames()
        return


class ConsumerThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super(ConsumerThread, self).__init__()
        self.target = target
        self.name = name
        return

    def run(self):
        while True:
            if not q.empty():
                convert_frames_to_gray_scale()
        return


def play_video():
    count = 0
    # load the frame
    frameFileName = "{}/frame_{:04d}.jpg".format(outputDir, count)
    frame = cv2.imread(frameFileName)
    startTime = time.time()

    while frame is not None:

        print("Displaying frame {}".format(count))
        # Display the frame in a window called "Video"
        cv2.imshow("Video", frame)

        # compute the amount of time that has elapsed
        # while the frame was processed
        elapsedTime = int((time.time() - startTime) * 1000)
        print("Time to process frame {} ms".format(elapsedTime))

        # determine the amount of time to wait, also
        # make sure we don't go into negative time
        timeToWait = max(1, frameDelay - elapsedTime)

        # Wait for 42 ms and check if the user wants to quit
        if cv2.waitKey(timeToWait) and 0xFF == ord("q"):
            break

            # get the start time for processing the next frame
        startTime = time.time()

        # get the next frame filename
        count += 1
        frameFileName = "{}/frame_{:04d}.jpg".format(outputDir, count)

        # Read the next frame file
        frame = cv2.imread(frameFileName)

    # make sure we cleanup the windows, otherwise we might end up with a mess
    cv2.destroyAllWindows()


def convert_frames_to_gray_scale():
    item = q.get()
    logging.debug('Getting frame ' + str(item)
                  + ' : ' + str(q.qsize()) + ' items in queue')

    # get the next frame file name
    inFileName = "{}/frame_{:04d}.jpg".format(outputDir, item)

    # load the next file
    inputFrame = cv2.imread(inFileName, cv2.IMREAD_COLOR)

    print("Converting frame {}".format(item))

    # convert the image to grayscale
    grayscaleFrame = cv2.cvtColor(inputFrame, cv2.COLOR_BGR2GRAY)

    # generate output file name
    outFileName = "{}/frame_{:04d}.jpg".format(outputDir, item)

    # write output file
    cv2.imwrite(outFileName, grayscaleFrame)

    item += 1

    # generate input file name for the next frame
    inFileName = "{}/frame_{:04d}.jpg".format(outputDir, item)


def extract_color_frames():
    if not os.path.exists(outputDir):
        print("Output directory {} didn't exist, creating".format(outputDir))
        os.makedirs(outputDir)

    # initialize frame count
    count = 0
    success, image = vidcap.read()
    # print("Putting frame {} {} ".format(count, success))
    while success:
        # write the current frame out as a jpeg image
        cv2.imwrite("{}/frame_{:04d}.jpg".format(outputDir, count), image)
        success, image = vidcap.read()
        q.put(count)
        logging.debug('Putting frame ' + str(count)
                      + ' : ' + str(q.qsize()) + ' items in queue')
        count += 1


if __name__ == '__main__':
    p = ProducerThread(name='producer')
    c = ConsumerThread(name='consumer')

    p.start()
    time.sleep(2)
    c.start()
    time.sleep(2)

    play_video()
