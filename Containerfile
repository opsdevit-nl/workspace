FROM alpine:3.16.2

ENV OC_VERSION=stable-4.11
ENV KUSTOMIZE_VERSION=v4.5.7
ENV KUBESEAL_VERSION=0.18.5

# layer for installing oc client
RUN wget https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/${OC_VERSION}/openshift-client-linux.tar.gz \
  && tar xvzf openshift-client-linux.tar.gz oc kubectl \
  && mv oc /usr/local/bin/oc \
  && mv kubectl /usr/local/bin/kubectl \
  && rm openshift-client-linux.tar.gz

# layer for kustomize
RUN wget https://github.com/kubernetes-sigs/kustomize/releases/download/kustomize%2F${KUSTOMIZE_VERSION}/kustomize_${KUSTOMIZE_VERSION}_linux_amd64.tar.gz \
  && tar xvf kustomize_${KUSTOMIZE_VERSION}_linux_amd64.tar.gz kustomize \
  && mv kustomize /usr/local/bin/kustomize \
  && rm kustomize_${KUSTOMIZE_VERSION}_linux_amd64.tar.gz

# layer for kubeseal
RUN wget https://github.com/bitnami-labs/sealed-secrets/releases/download/v${KUBESEAL_VERSION}/kubeseal-${KUBESEAL_VERSION}-linux-amd64.tar.gz \
  && tar xvf kubeseal-${KUBESEAL_VERSION}-linux-amd64.tar.gz kubeseal \
  && mv kubeseal /usr/local/bin/kubeseal \
  && rm kubeseal-${KUBESEAL_VERSION}-linux-amd64.tar.gz

WORKDIR /ansible

# layers for installing dependencies for Ansbile
COPY ./apk-packages-world.list ./apk-packages-virtual.list ./
RUN apk update \
  && apk add --no-cache --progress $(cat apk-packages-world.list) \
  && apk add --progress --update --virtual build-dependencies $(cat apk-packages-virtual.list) \
  && rm -rf /var/cache/apk/* \
  && apk list --installed > /apk-freeze.txt 

# layers for installing Ansible
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
