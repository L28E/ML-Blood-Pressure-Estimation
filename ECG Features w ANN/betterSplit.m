% This script is able to split the data into train and and test data set.
% After spliting the data into train and test data set, the "fitrnet"
% command will help to train the machine learning model and changing
% parameters and with set of parameters with the lowest mean absolute error
% with be stored in the variable "MDL" and that variable can be saved in
% your workspace and working directory and re-used over and over by calling
% the model into the new workspace

clc; clear all;
A = importdata("ecg_FeaturesNew.csv"); %Import your data
B = A.data;
data = B;

%Split the data into training and testing set
cv =  cvpartition(size(data,1),'HoldOut',0.3);
idx = cv.test;

dataTrain = data(~idx,:);
dataTest = data(idx,:);

train = dataTrain(:,3:29);
systrain = dataTrain(:,1);
dialtrain = dataTrain(:,2);

test = dataTest(:,3:29);
systest = dataTest(:,1);
dialtest = dataTest(:,2);

%Specifies the parameter that will be optimized for the particular value
%you want to predict
params = hyperparameters("fitrnet",train,dialtrain);
%for ii = 1:length(params)
    %disp(ii);disp(params(ii))
%end

params(1).Range = [1 5];
params(10).Optimize = true;
params(11).Optimize = true;
for ii = 7:11
    params(ii).Range = [1 400];
end

% MODELS
%For Diastolic BP
%Algorithm to generate the best model with the best accuracy. 
Mdl = fitrnet(train,dialtrain,"OptimizeHyperparameters",params, ...
    "HyperparameterOptimizationOptions", ...
    struct("AcquisitionFunctionName","expected-improvement-plus", ...
    "MaxObjectiveEvaluations",60), Standardize=true)
%ypred = predict(Mdl,test);
%mae(ypred - systest)


params2 = hyperparameters("fitrnet",train,systrain);
%for ii = 1:length(params)
    %disp(ii);disp(params(ii))
%end

params2(1).Range = [1 5];
params2(10).Optimize = true;
params2(11).Optimize = true;
for ii = 7:11
    params2(ii).Range = [1 400];
end

% MODELS
%For Systolic BP
Mdl2 = fitrnet(train,systrain,"OptimizeHyperparameters",params2, ...
    "HyperparameterOptimizationOptions", ...
    struct("AcquisitionFunctionName","expected-improvement-plus", ...
    "MaxObjectiveEvaluations",60), Standardize=true)
%ypred = predict(Mdl,test);
%mae(ypred - systest)