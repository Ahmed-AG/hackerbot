FROM python

RUN apt-get update 

# Install security tools
RUN apt install nmap netcat -y
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && unzip awscliv2.zip && ./aws/install

# Install Metasploit
# RUN curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall && chmod 755 msfinstall && ./msfinstall

# Create and use local user
RUN groupadd -r hb && useradd -r -g hb -m -d /home/hb -s /bin/bash hb
RUN chown -R hb:hb /home/hb && chmod 755 /home/hb
USER hb

# Install Required Python packages
RUN pip install langchain colorama boto3 chromadb google-search-results tiktoken openai

# CLone hackerBot
RUN cd ~ && git clone https://github.com/Ahmed-AG/hackerbot.git

CMD cd ~/hackerbot && python3 hb.py