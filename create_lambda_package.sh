#!/bin/bash

BASEDIR=$(pwd)
rm -rf $BASEDIR/lambda_package.zip
cd  $BASEDIR/lambda/codeCounterEnv/lib/python3.6/site-packages/
zip -r9 $BASEDIR/lambda_package.zip *
cd $BASEDIR/lambda/codeCounterEnv/lib64/python3.6/site-packages/
zip -r9 $BASEDIR/lambda_package.zip *
cd $BASEDIR/lambda

zip -r9 $BASEDIR/lambda_package.zip codeCounter_classes_lambda.py

sudo cp lambda_package.zip /media/sf_MintShared
