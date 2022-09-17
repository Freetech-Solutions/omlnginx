#!/bin/bash
PACKAGE_VERSION=$(cat ../../.package_version)

echo "Installing nginx"
yum install -y nginx nginx-all-modules
cd /builds/omnileads/omlnginx
echo "Copying configuration folder to /etc/nginx/"
mkdir -p /etc/nginx/conf.d
cp -a source/conf/conf.d/ominicontacto.conf /etc/nginx/conf.d
cp -a source/conf/mime.types source/conf/nginx.conf source/conf/uwsgi_params /etc/nginx
echo "Running set_environment.sh script"
INFRA=onpremise ENV=prodenv ./source/set_environment.sh

echo "Packing the rpm"
fpm -s dir -t rpm -n nginx -v ${PACKAGE_VERSION} -d openssl11-libs -d gd -d gperftools-libs -d libXpm -d libxslt \
  --before-install build/rpm/scripts/before_install.sh \
  --after-install build/rpm/scripts/after_install.sh \
  --after-remove build/rpm/scripts/after_remove.sh \
  -f /etc/nginx/ \
  /etc/logrotate.d/nginx \
  /var/lib/nginx \
  /var/log/nginx \
  /usr/bin/nginx-upgrade \
  /usr/sbin/nginx \
  build/rpm/nginx.service=/etc/systemd/system/nginx.service \
  /usr/lib64/perl5/vendor_perl/auto/nginx/nginx.so \
  /usr/lib64/perl5/vendor_perl/nginx.pm \
  /usr/lib64/nginx \
  /usr/share/nginx
mv nginx-${PACKAGE_VERSION}* /root
echo "Uploading rpm to AWS repository"
aws s3 cp /root/nginx* s3://${AWS_BUCKET}/nginx/nginx-omnileads-${PACKAGE_VERSION}.x86_64.rpm
