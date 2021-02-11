#!/bin/bash
pwd
if [[ $CI_COMMIT_REF_NAME == *"release"* ]]; then
  BRANCH=$(echo $CI_COMMIT_REF_NAME|awk -F '-' '{print $2}')
elif [ $CI_COMMIT_REF_NAME == "master" ]; then
  BRANCH="master"
elif [ $CI_COMMIT_REF_NAME == "develop" ]; then
  BRANCH="develop"
elif [[ $CI_COMMIT_REF_NAME == *"oml-"* ]]; then
  BRANCH=$(echo $CI_COMMIT_REF_NAME|awk -F '-' '{print $2}')
  BRANCH=$(echo ${BRANCH:0:2}.${BRANCH})
fi

echo "Installing nginx"
yum install -y nginx nginx-all-modules
echo "Copying configuration folder to /etc/nginx/"
cp -a conf/* /etc/nginx/
echo "Running set_environment.sh script"
./scripts/set_environment.sh
echo "Packing the rpm"
cd /root/
fpm -s dir -t rpm -n nginx -v ${BRANCH} -d openssl11-libs -d gd -d centos-logos -d gperftools-libs -d libXpm -f /etc/nginx/ \
  /etc/logrotate.d/nginx \
  /var/lib/nginx \
  /var/log/nginx \
  /usr/bin/nginx-upgrade \
  /usr/sbin/nginx \
  /builds/omnileads/omlnginx/nginx.service=/etc/systemd/system/nginx.service \
  /usr/lib64/perl5/vendor_perl/auto/nginx/nginx.so \
  /usr/lib64/perl5/vendor_perl/nginx.pm \
  /usr/lib64/nginx \
  /usr/share/nginx \

echo "Uploading RPM to AWS repository"
echo "Uploading rpm to s3 bucket"
aws s3 cp nginx* s3://${AWS_BUCKET}/nginx/nginx-omnileads-${BRANCH}.x86_64.rpm
