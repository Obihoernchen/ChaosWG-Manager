# ChaosWG-Manager
[![Build Status](https://scrutinizer-ci.com/g/Obihoernchen/ChaosWG-Manager/badges/build.png?b=master)](https://scrutinizer-ci.com/g/Obihoernchen/ChaosWG-Manager/build-status/master) [![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/Obihoernchen/ChaosWG-Manager/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/Obihoernchen/ChaosWG-Manager/?branch=master) ![Python 3](https://img.shields.io/badge/python-3-blue.svg) [![License](https://img.shields.io/badge/license-AGPLv3-blue.svg)](https://github.com/Obihoernchen/ChaosWG-Manager/blob/master/LICENSE)

ChaosWG-Manager is a living community planner.

![Screenshot](https://cdn.rawgit.com/Obihoernchen/ChaosWG-Manager/855714eb/Screenshot.png)

## TODO
- use AJAX so we don't have to reload the whole page (single page with dynamic content)
- proper timezone support
- task interval (auto set to todo)
- use jinja2 dictsort for tasks?
- delete task button
- optimize the users=User.get_all() on all templates (cache it or something).
- get task history from history table for each task and show in details (who did the task and when)
- y-axis left and right
- absence considerations
