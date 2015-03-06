# gitlab-webhooks

Daemon uses to execute shell script upon gitlab repository push event.

Use `config.yaml` to configure daemon to execute a shell script when a branch of a given repository is updated.

You can either user `receiver.py` directly or use the init.d service script provided.

```yaml
hooks:                                          
    -                                           
        name: 'Project Name'                    
        repository: project                     
        branch: develop                         
        directory: /repository/folder           
        script: scripts/laravel.frontend.sh     
        env:                                    
            LARAVEL_ENV: design                 
            DEPLOY_KEY: ~/.ssh/deploy_rsa       
                                                
logs:                                           
        file: /tmp/webhook.log                  
        max_size: 25165824 # 24 Mb              
        level: DEBUG                            
                                                
```

***
Inspired by https://github.com/shawn-sterling/gitlab-webhook-receiver
