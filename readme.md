## ubuntu install
sudo apt update && sudo apt upgrade -y
# install python and git
sudo apt install python3 python3-pip -y
sudo apt install git -y
sudo apt install python3-venv
## config git
git config --global user.name "Tu Nombre"
git config --global user.email "tu.email@example.com"

# creacion entorno virtual
python3 -m venv venv
# activacion entorno
source venv/bin/activate
# instalacion bibliotecas
pip install discord.py aiosqlite fastapi uvicorn

# crear repositorio git
git init

# crear git ignore
echo "venv/" > .gitignore
echo "*.db" >> .gitignore
echo "__pycache__/" >> .gitignore
echo ".vscode/" >> .gitignore

# crear primer commit + add
git add .
git commit -m "Configuración inicial del proyecto y .gitignore"
git remote add (name) (url)
git push -set-upstream origin master
git pull
git push -u origin (loc)
git checkout master(navigate)
git checkout -b (branch)@bot.command()

pull request

# bot1
un bot que toma el valor con +200, luego va y update la base de datos actualizando de acuerdo a si es suma y resta, con una funcion para reiniciar su valor, y una funcion de historial que muestra el historial en formato ascii

# bo2
un bot que toma el comando !calcular 100, y ese numero lo multiplica por una variable que se coloca en el canal y queda anclada a este y se puede reemplazar solo utilizando un comando, esto dará un embed, donde se tomará la decision de guardar transaccion o cancelar transaccion, esto con una ruta de base de datos ya predispuesta

propuesta, unificar ambos bot