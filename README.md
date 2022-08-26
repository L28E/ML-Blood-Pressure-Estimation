# About
This is our capstone project; Estimating Blood Pressure by Applying Machine Learning to PPG and ECG Signals. The project is complete, but this repo is still a WIP. 

ECG and PPG stand for electrocardiograph and photoplethesmograph respectively. An ECG is a measure of electrical activity in the heart, while a PPG is an optical measurement of relative changes in blood volume at some site on the body. 

Blood pressure is a vital sign, something we look for as an indicator of health, not unlike heart rate. A key difference however is that there is a well-defined relationship between an ECG trace and heart rate, but such an explicit relationship does not exist for blood pressure. Instead, we use machine learning to try and extrapolate a relationship using features of the data which have some correlation with blood pressure.

The conventional method of measuring blood pressure with a sphygmomanometer has a lot of friction in both a literal and figurative sense, as the cuff is prohibitive to measuring one's blood pressure continuously. ECG and PPG signals can be observed more conveniently, and by leveraging machine learning, we can estimate blood pressure using the aforementioned signals. By increasing the convenience and ease with which blood pressure can be measured (or at least estimated), patients may be inclined to measure their blood pressure more frequently, thus better monitoring their cardiovascular health.

# Method
At a high-level, our machine learning workflow was as follows:
- Pre-process the data to remove noise from several potential sources
- Perform calculations on the signal to extract potentially relevant information, hence feature extraction
- Determine which features are the best predictors, hence feature selection
- Train, test and optimize our machine learning models. There are a lot of "knobs and dials" so to speak, so improving prediction accuracy was an iterative process

Pre-processing and feature extraction for ECG and PPG are found in [ECG Feature Extraction](/ECG%20Feature%20Extraction/) and [PPG Feature Extraction](/PPG%20Feature%20Extraction/) respectively


Each team member explored a different combination of signal type and machine learning model, resulting in 4 permutations of the workflow:
- [ECG Features with ANN](/ECG%20Features%20w%20ANN/)
- [ECG Features with Random Forest Regression](/ECG%20Features%20w%20Random%20Forest%20Regression/)
- [PPG Features with ANN](/PPG%20Features%20w%20ANN/)
- [PPG Features with Random Forest Regression](/PPG%20Features%20w%20Random%20Forest%20Regression/)

# Dependencies
* numpy, pandas, and scipy (for manipulating large data structures) 
* matplotlib (for visualization) 
* neurokit2 (for biosignal processing) 
* pywavelets (for wavelet based transformations) 
* antropy (for calculating entropy)

Install them all with `pip3 install numpy pandas scipy matplotlib neurokit2 PyWavelets antropy`

