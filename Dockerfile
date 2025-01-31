FROM python:3.9-bookworm

RUN pip3 install --upgrade pip \
    && pip3 install poetry \
    && pip3 install pre-commit

COPY ./pyproject.toml ./poetry.lock* /

RUN poetry config virtualenvs.create false \
    && poetry lock --no-update \
    && poetry install --no-dev --no-interaction --no-ansi --no-root

RUN apt-get update && \
  apt-get install -y sudo \
  git-core \
  zsh \
  wget \
  fonts-powerline

ENV SHELL /bin/zsh

RUN wget https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | zsh || true

# install powerlevel10k
RUN git clone https://github.com/romkatv/powerlevel10k.git ~/.oh-my-zsh/custom/themes/powerlevel10k

RUN cd $HOME && curl -fsSLO https://raw.githubusercontent.com/romkatv/dotfiles-public/master/.purepower

# zsh configuration
ADD /.devcontainer/.zshrc $HOME
