import cv2
import matplotlib.pyplot as plt
import numpy as np
import imutils
import easyocr


def get_str(JSON):
    # Return json formatted for showing (no json.dumps..)
    st = ''

    for key in JSON:
        st += f'{key}: {JSON[key]}\n'

    return st


# Module for detecting plate's number
class PlateDetector:

    # Constructor
    def __init__(self, image_path):
        # Set image as path
        self.image = cv2.imread(image_path)
        self.gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.mispar = ''
        self.res = self.image

        # Begin detection
        self.grayfy(self.gray)

    # Make the image with gray bi-lateral filter
    def grayfy(self, gray):
        bfilter = cv2.bilateralFilter(gray, 11, 17, 17)  # Noise reduction
        edged = cv2.Canny(bfilter, 30, 200)  # Edge detection

        # Find key points
        self.find_key_points(edged)

    def find_key_points(self, edged):
        keypoints = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(keypoints)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

        # Find location of contours in image
        self.find_location(contours)

    def find_location(self, contours):
        location = None
        for contour in contours:
            approx = cv2.approxPolyDP(contour, 10, True)
            if len(approx) == 4:
                location = approx
                break

        # Finalize the actions
        self.finish(location, approx)

    def finish(self, location, approx):
        mask = np.zeros(self.gray.shape, np.uint8)
        new_image = cv2.drawContours(mask, [location], 0, 255, -1)
        new_image = cv2.bitwise_and(self.image, self.image, mask=mask)

        plt.imshow(cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB))

        (x, y) = np.where(mask == 255)
        (x1, y1) = (np.min(x), np.min(y))
        (x2, y2) = (np.max(x), np.max(y))
        cropped_image = self.gray[x1:x2 + 1, y1:y2 + 1]

        reader = easyocr.Reader(['en'])
        result = reader.readtext(cropped_image)

        text = result[0][-2].replace(".", "").replace("*", "").replace(",", "")

        # Set vehicle's number as found text
        self.set_car_id(text)
        print(self.mispar)

        font = cv2.FONT_HERSHEY_SIMPLEX
        res = cv2.putText(self.image, text=text, org=(approx[0][0][0], approx[1][0][1] + 60), fontFace=font, fontScale=1,
                          color=(0, 255, 0), thickness=2, lineType=cv2.LINE_AA)

        res = cv2.rectangle(self.image, tuple(approx[0][0]), tuple(approx[2][0]), (0, 255, 0), 3)

        self.res = res

        plt.imshow(cv2.cvtColor(res, cv2.COLOR_BGR2RGB))
        plt.show()

    def get_res(self):
        return self.res

    def set_car_id(self, text):
        # Set vehicle's number
        self.mispar = text

    def get_car_info(self):
        # Import http requests lib
        import requests

        # API's URL
        url = f'https://data.gov.il/api/3/action/datastore_search?' \
              f'resource_id=053cea08-09bc-40ec-8f7a-156f0677aff3&' \
              f'limit=1&' \
              f'q={self.mispar}'

        # API response
        file_obj = requests.request('GET', url)

        # Return vehicle's info
        return file_obj.json()['result']['records'][0]
