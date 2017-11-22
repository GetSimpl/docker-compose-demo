# docker-compose-demo

A sample app used to demonstrate `cloudlift` session.

**Prerequisties:**

- Docker


**To run:**

```
# Cloning with a unique name ensures when you deploy there's no conflict
git clone git@github.com:GetSimpl/docker-compose-demo.git <yourname>-sample

cd <yourname>-sample

cp env.sample development.env

docker-compose up

```

Now visit http://localhost:8080/
