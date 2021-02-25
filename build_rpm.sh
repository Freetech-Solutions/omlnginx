#!/bin/bash
PACKAGE_VERSION=$(cat .package_version)

echo "Installing nginx"
yum install -y nginx nginx-all-modules
echo "Copying configuration folder to /etc/nginx/"
cp -a conf/* /etc/nginx/
echo "Running set_environment.sh script"
./scripts/set_environment.sh
if [ ! -d /opt/omnileads/nginx_certs ]; then
  mkdir -p /opt/omnileads/nginx_certs
fi
echo "Adding the certificates"
cp -a /builds/omnileads/omlnginx/certs/* /opt/omnileads/nginx_certs
echo "Packing the rpm"
cd /root/
fpm -s dir -t rpm -n nginx -v ${PACKAGE_VERSION} -d openssl11-libs -d gd -d centos-logos -d gperftools-libs -d libXpm \
  --after-install /builds/omnileads/omlnginx/scripts/after_install.sh \
  --after-remove /builds/omnileads/omlnginx/scripts/after_remove.sh \
  -f /etc/nginx/ \
  /etc/logrotate.d/nginx \
  /opt/omnileads/nginx_certs \
  /var/lib/nginx \
  /var/log/nginx \
  /usr/bin/nginx-upgrade \
  /usr/sbin/nginx \
  /builds/omnileads/omlnginx/nginx.service=/etc/systemd/system/nginx.service \
  /usr/lib64/perl5/vendor_perl/auto/nginx/nginx.so \
  /usr/lib64/perl5/vendor_perl/nginx.pm \
  /usr/lib64/nginx \
  /usr/share/nginx

echo "Uploading rpm to AWS repository"
aws s3 cp nginx* s3://${AWS_BUCKET}/nginx/nginx-omnileads-${PACKAGE_VERSION}.x86_64.rpm
