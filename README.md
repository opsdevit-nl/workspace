# workspace

see https://hub.docker.com/repository/docker/rsg4a/workspace-container

## generate ansible vault password hash
```
read -s NEW_ANSIBLE_VAULT_PASS
echo "${NEW_ANSIBLE_VAULT_PASS}" | openssl enc -e -aes256 -md sha512 -pbkdf2 -iter 100000 -a -salt
```

## add to ~/.bashrc
```
export ANSIBLE_VAULT_PASSWORD=$(echo "<HASH>" | openssl enc -d -aes256 -md sha512 -pbkdf2 -iter 100000 -a -salt)
alias ws-container="podman run --rm -v "~/Projects/Ansible":/ansible:Z -v ~/.kube/config:/ansible/.kube/config:Z -e ANSIBLE_VAULT_PASSWORD=${ANSIBLE_VAULT_PASSWORD} --entrypoint='' workspace-container"
alias oc="ws-container oc"
alias kubectl="ws-container kubectl"
alias kustomize="ws-container kustomize"
alias kubeseal="ws-container kubeseal"
```
> NOTE: The export line will cause a hanging logon session after logging in to GNOME or KDE
>       This is because it initializes ~/.bashrc. Just press (an extra Enter) after logging in
