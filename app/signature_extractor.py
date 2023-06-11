import cv2
import matplotlib.pyplot as plt
from skimage import measure, morphology
from skimage.measure import regionprops
import numpy as np

# the parameters are used to remove small size connected pixels outliar 
constant_parameter_1 = 84
constant_parameter_2 = 250
constant_parameter_3 = 100

# the parameter is used to remove big size connected pixels outliar
constant_parameter_4 = 18

def count_signatures(image):
    # Convert the image to binary
    _, binary_image = cv2.threshold(image, 1, 255, cv2.THRESH_BINARY)

    # Perform connected component analysis
    num_labels, labels_im = cv2.connectedComponents(binary_image)

    return num_labels - 1 

def extract_signature(source_image, min_area=100, kernel_size=(1, 1)):
    """Extract signature from an input image.

    Parameters
    ----------
    source_image : numpy ndarray
        The pinut image.

    Returns
    -------
    numpy ndarray
        An image with the extracted signatures.

    """
    # read the input image
    img = source_image
    img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)[1]  # ensure binary

    # connected component analysis by scikit-learn framework
    blobs = img > img.mean()
    blobs_labels = measure.label(blobs, background=1)
    # image_label_overlay = label2rgb(blobs_labels, image=img)

    fig, ax = plt.subplots(figsize=(10, 6))

    '''
    # plot the connected components (for debugging)
    ax.imshow(image_label_overlay)
    ax.set_axis_off()
    plt.tight_layout()
    plt.show()
    '''

    the_biggest_component = 0
    total_area = 0
    counter = 0
    average = 0.0
    for region in regionprops(blobs_labels):
        if (region.area > 10):
            total_area = total_area + region.area
            counter = counter + 1
        # print region.area # (for debugging)
        # take regions with large enough areas
        if (region.area >= 250):
            if (region.area > the_biggest_component):
                the_biggest_component = region.area

    average = (total_area/counter)
    print("the_biggest_component: " + str(the_biggest_component))
    print("average: " + str(average))

    a4_small_size_outliar_constant = ((average/constant_parameter_1)*constant_parameter_2)+constant_parameter_3
    print("a4_small_size_outliar_constant: " + str(a4_small_size_outliar_constant))

    a4_big_size_outliar_constant = a4_small_size_outliar_constant*constant_parameter_4
    print("a4_big_size_outliar_constant: " + str(a4_big_size_outliar_constant))

    # remove the connected pixels are smaller than a4_small_size_outliar_constant
    pre_version = morphology.remove_small_objects(blobs_labels, a4_small_size_outliar_constant)

    component_sizes = np.bincount(pre_version.ravel())
    too_small = component_sizes > (a4_big_size_outliar_constant)
    too_small_mask = too_small[pre_version]
    pre_version[too_small_mask] = 0
    # save the the pre-version which is the image is labelled with colors
    plt.imsave('pre_version.png', pre_version)

    # read the pre-version
    img = cv2.imread('pre_version.png', 0)
    # ensure binary
    img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    # save the the result
    # cv2.imwrite("output.png", img)
    num_signatures = count_signatures(img)
    kernel = np.ones(kernel_size, np.uint8)
    dilated = cv2.dilate(img, kernel, iterations = 1)
    morph_closed = cv2.erode(dilated, kernel, iterations = 1)

    # Use connectedComponentsWithStats to count the number of connected components
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(morph_closed, connectivity=8)
    
    # Filter out small components based on area
    large_components = np.zeros_like(labels)
    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] >= min_area:
            large_components[labels == i] = 255
    
    large_components = large_components.astype(np.uint8)

    # Recount the number of components
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(large_components, connectivity=8)
    num_signatures = num_labels - 1 

    return large_components, num_signatures

