#! /bin/bash
cd $1
git reset --hard HEAD
git checkout $2
ssh-agent bash -c "ssh-add $DEPLOY_KEY; git pull origin $2; git submodule update"
/servers/apache/php/bin/php artisan assetic:build
/servers/apache/php/bin/php artisan twig:clean
/servers/apache/php/bin/php artisan twig:warmup

