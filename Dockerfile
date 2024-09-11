FROM node:16
WORKDIR /app
RUN apt update
RUN apt install python3-pip

RUN pip install numpy
RUN pip install sympy
RUN pip install pytexit

RUN npm install body-parser
RUN npm install express
COPY package-lock.json ./
RUN npm install package-lock.json
COPY . .
CMD ["npm", "start"]