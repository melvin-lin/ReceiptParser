### A Receipt Parser Using Google Vision API and OpenCV

The parser intakes a input directory that finds the corners for each respective receipt, applies a four-point perspective transformation, creates a python dictionary from the annotations from the Google Vision API for the receipts, and outputs the parsed values into a .csv file called receipt.csv. This project utilizes a GitHub repository called [OpenCV-Document-Scanner](https://github.com/andrewdcampbell/OpenCV-Document-Scanner) to scan the receipts. The code was modified accordingly based on whether the receipt was printed with a non-white underside or not to apply the adaptive color threshold. Most receipts only required the cropping and gray-scaling. In addition, the use of the Google Vision API was rooted in a [medium article](https://betterprogramming.pub/google-vision-and-google-sheets-api-line-by-line-receipt-parsing-2e2661261cda). 

### Motivation

Because of the multiple shopping/grocery trips taken and the number of people that were grouped onto the same receipts, we needed a more efficient way to distribute charges amongst the group of people that shared the receipts. Currently, the method that is used by our group is manually inputting the data into an Excel sheet. 

### Datasets

Because the datasets that were found online had items blurred out, watermarks, and other 
My test dataset consisted of receipts gathered from my friends in the past few weeks, which resulted in Star Market, TJ Maxx, H-Mart, Tufts University Bookstore, Hillsides Wine and Spirits receipts, and many others. 

### Deliverables
* Utilize Natural Language Processing (NGL) and Image Processing to parse through the receipt
* Ensure that the parser works on a variety of receipts
* Creates an Excel sheet from the parsered receipts
* Presentation and demo of the Receipt Parser

### Usage
Before running, you want to modify the interface.py: 
```
SRC_DIR = "PATH"
```
to path of the output directory generated by scan.py in interface.py. 


To run the Receipt Parser: 
```
python interface.py
```
* All receipt images should be inputted into the directory called input. 
* The scanned receipts will then be outputted into a directory called output. 
* extraction.py uses Google API to parse the scanned receipts and then the application of NGL as I created my own algorithm to extract information from the receipts. 
* A .csv file called receipt.csv will be generated and contain specific elements from the receipts with labelled columns. 


### Known Current Issues
* NGL algorithm Issues:
  *  Strings that are located below barcodes or at the bottom of receipt that contain date and time are unable to be retrieved
  *  Inability for algorithm to 
     *  Determine street addresses
     *  Whether there or not there is an additional part to the name of the market on the second line of the receipt
  *  Unable to distinguish between formats shown in Bfresh and Stop & Shop Receipts, where the actual price is listed as the "discount" or "price you pay"

 





