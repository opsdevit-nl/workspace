FROM alpine:3.16.2

ENV OC_VERSION=stable-4.11
ENV KUSTOMIZE_VERSION=v4.5.7

# layer for installing dependencies for Ansbile
RUN apk update \
  && apk add --no-cache --progress python3 openssl ca-certificates git openssh sshpass \
  && apk --progress --update add --virtual build-dependencies \
  python3-dev py3-pip libffi-dev openssl-dev build-base bash curl wget tar gcompat \
  && rm -rf /var/cache/apk/* 

# layer for installing oc client
RUN wget https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/${OC_VERSION}/openshift-client-linux.tar.gz \
  && tar xvzf openshift-client-linux.tar.gz \
  && mv oc /usr/local/bin/oc \
  && chmod +x /usr/local/bin/oc \
  && mv kubectl /usr/local/bin/kubectl \
  && chmod +x /usr/local/bin/kubectl \
  && rm README.md openshift-client-linux.tar.gz

# layer for kustomize
RUN wget https://github.com/kubernetes-sigs/kustomize/releases/download/kustomize%2F${KUSTOMIZE_VERSION}/kustomize_${KUSTOMIZE_VERSION}_linux_amd64.tar.gz \
  && tar xvf kustomize_v4.5.7_linux_amd64.tar.gz \
  && mv kustomize /usr/local/bin/kustomize

WORKDIR /ansible

# layer for installing Ansible
COPY ./pip-requirements.txt pip-requirements.txt
RUN pip3 install --upgrade pip \
  && pip3 install -r pip-requirements.txt \ 
  && pip3 list --format=freeze > /pip-freeze.txt 

COPY ./requirements.yml requirements.yml
RUN ansible-galaxy install -r requirements.yml

ENV KUBECONFIG=/ansible/.kube/config
ENV ANSIBLE_VAULT_PASSWORD_FILE=/ansible/vaultpass

COPY ./entrypoint.sh entrypoint.sh
ENTRYPOINT ["bash","entrypoint.sh"]
