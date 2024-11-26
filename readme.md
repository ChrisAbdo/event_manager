## HW10 - Chris Abdo

## Issues
- Username Validation (https://github.com/ChrisAbdo/event_manager/issues/1)
- Password Validation (https://github.com/ChrisAbdo/event_manager/issues/2)
- Profile Edge Cases (https://github.com/ChrisAbdo/event_manager/issues/3)
- Email (https://github.com/ChrisAbdo/event_manager/issues/4)
- User roles (https://github.com/ChrisAbdo/event_manager/issues/5)

## Link to Dockerhub
- Dockerhub (https://hub.docker.com/repository/docker/chrisabdo/hw10-fast/general)

## What I Learned
This was a great assignment to learn and practice how to efficiently set up authentication systems and learn how to pull everything together using docker to make a fully comprehensive suite that includes testing and running everything locally. Figuring out how to initially set up the pgAdmin dashboard and the localhost/docs was a little tricky since I kept running into issues with authenticating. I was able to solve this by performing the migration and then pushing to the db and then rebuilding my docker image. Upon loading the localhost/docs site I was able to sign in successfully and not get the internal server error. Setting up pgAdmin was very informative because I have never set up a local postgres instance before. It was cool learning about the whole dashboard and figuring out how to query for information through there. Improving validation also was a pretty hard task as that required some rewriting of the original functionality to account for new regex patterns and everything to strengthen the username validation portion. As for password validation, that was relatively simple as it just required adding some required props to the submission such as a required length of using certain characters like uppercase, lowercase, and specials.

Creating the tests was a very beneficial way of understanding how it actually goes into play. There were many times I made new test files but they completely failed since I forgot to account for every single new validation we introduced. The tests aim to make sure that the validations introduced are working properly so users do not run into issues while trying to sign up or login or do anything with an authentication-lock on it. password hashing and JWT tokens along with newly introduced stronger role-based access gives the platform a much more comprehensive and safe authentication process. In addition, the containerized setup made it super easy to make some code changes and instantly seeing it being reflected in the dashboard. Overall, this assignment was fantastic for learning how to combine everything to get a fairly complex yet simple system going on using Docker, pgAdmin, and fast-api to build a comprehensive authentication setup.
