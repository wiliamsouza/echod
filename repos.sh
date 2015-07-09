#!/bin/bash

git remote add github git@github.com:wiliamsouza/echo.git
git remote add bitbucket git@bitbucket.org:wiliamsouza/echo.git
git remote add gitlab git@gitlab.com:wiliamsouza/echo.git
git remote add notabug git@notabug.org:wiliamsouza/echo.git
git remote set-url --push --add origin git@bitbucket.org:wiliamsouza/echo.git
git remote set-url --push --add origin git@gitlab.com:wiliamsouza/echo.git
git remote set-url --push --add origin git@github.com:wiliamsouza/echo.git
git remote set-url --push --add origin git@notabug.org:wiliamsouza/echo.git
