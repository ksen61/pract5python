from flask import Flask, render_template, request, redirect, url_for, flash, session
from web3 import Web3
from web3.middleware import geth_poa_middleware
from contract_info import abi, contract_address

app = Flask(__name__)
app.secret_key = 'your_secret_key'

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

contract = w3.eth.contract(address=contract_address, abi=abi)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        public_key = request.form['public_key']
        password = request.form['password']
        try:
            w3.geth.personal.unlock_account(public_key, password)
            session['account'] = public_key
            flash(f"Аккаунт авторизован: {public_key}", 'success')
            return redirect(url_for('menu'))
        except Exception as e:
            flash(f"Ошибка авторизации: {str(e)}", 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        password = request.form['password']
        if (len(password) < 12 or
            not any(c.isupper() for c in password) or
            not any(c.islower() for c in password) or
            not any(c.isdigit() for c in password) or
            not any(c in "!@#$%^&*()-_+=" for c in password)):
            flash("Пароль не удовлетворяет требованиям", 'danger')
        else:
            try:
                account = w3.geth.personal.new_account(password)
                flash(f"Аккаунт создан: {account}", 'success')
                return redirect(url_for('menu'))
            except Exception as e:
                flash(f"Ошибка создания аккаунта: {str(e)}", 'danger')
    return render_template('register.html')

@app.route('/menu')
def menu():
    if 'account' not in session:
        flash("Пожалуйста, войдите в аккаунт", 'danger')
        return redirect(url_for('login'))
    return render_template('menu.html', account=session['account'])

@app.route('/createestate', methods=['GET', 'POST'])
def createestate():
    if 'account' not in session:
        flash("Пожалуйста, войдите в аккаунт", 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        account = session['account']
        size = int(request.form['size'])
        address = request.form['address']
        estype = int(request.form['estype'])
        try:
            tx_hash = contract.functions.createestate(size, address, estype).transact({'from': account})
            flash(f"Запись о недвижимости успешно создана. Транзакция отправлена: {tx_hash.hex()}", 'success')
        except Exception as e:
            flash(f"Ошибка создания записи о недвижимости: {str(e)}", 'danger')
    return render_template('createestate.html')

@app.route('/createad', methods=['GET', 'POST'])
def createad():
    if 'account' not in session:
        flash("Пожалуйста, войдите в аккаунт", 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        account = session['account']
        try:
            idestate = int(request.form['idestate'])
            price = int(request.form['price'])
            tx_hash = contract.functions.createad(idestate, price).transact({'from': account})
            flash(f"Объявление о продаже недвижимости успешно создано. Транзакция отправлена: {tx_hash.hex()}", 'success')
        except KeyError as e:
            flash(f"Ошибка: отсутствует ключ {str(e)}", 'danger')
        except Exception as e:
            flash(f"Ошибка создания объявления о продаже недвижимости: {str(e)}", 'danger')
    return render_template('createad.html')


@app.route('/changeestatestatus', methods=['GET', 'POST'])
def changeestatestatus():
    if 'account' not in session:
        flash("Пожалуйста, войдите в аккаунт", 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        account = session['account']
        idestate = int(request.form['idestate'])
        try:
            tx_hash = contract.functions.changeestatestatus(idestate).transact({'from': account})
            flash(f"Статус недвижимости успешно изменен. Транзакция отправлена: {tx_hash.hex()}", 'success')
        except Exception as e:
            flash(f"Ошибка изменения статуса недвижимости: {str(e)}", 'danger')
    return render_template('changeestatestatus.html')

@app.route('/changeadstatus', methods=['GET', 'POST'])
def changeadstatus():
    if 'account' not in session:
        flash("Пожалуйста, войдите в аккаунт", 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        account = session['account']
        idad = int(request.form['idad'])
        try:
            tx_hash = contract.functions.changeadstatus(idad).transact({'from': account})
            flash(f"Статус объявления успешно изменен. Транзакция отправлена: {tx_hash.hex()}", 'success')
        except Exception as e:
            flash(f"Ошибка изменения статуса объявления: {str(e)}", 'danger')
    return render_template('changeadstatus.html')

@app.route('/buyestate', methods=['GET', 'POST'])
def buyestate():
    if 'account' not in session:
        flash("Пожалуйста, войдите в аккаунт", 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        account = session['account']
        try:
            idestate = int(request.form['idestate'])
            tx_hash = contract.functions.buyestate(idestate).transact({'from': account})
            flash(f"Покупка недвижимости успешно завершена. Транзакция отправлена: {tx_hash.hex()}", 'success')
        except KeyError as e:
            flash(f"Ошибка: отсутствует ключ {str(e)}", 'danger')
        except Exception as e:
            flash(f"Ошибка покупки недвижимости: {str(e)}", 'danger')
    return render_template('buyestate.html')


@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if 'account' not in session:
        flash("Пожалуйста, войдите в аккаунт", 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        account = session['account']
        amount = int(request.form['amount'])
        try:
            tx_hash = contract.functions.withdraw(amount).transact({'from': account})
            flash(f"Средства успешно выведены. Транзакция отправлена: {tx_hash.hex()}", 'success')
        except Exception as e:
            flash(f"Ошибка вывода средств: {str(e)}", 'danger')
    return render_template('withdraw.html')

@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if 'account' not in session:
        flash("Пожалуйста, войдите в аккаунт", 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        account = session['account']
        amount = int(request.form['amount'])
        try:
            tx_hash = contract.functions.deposit().transact({'from': account, 'value': amount})
            flash(f"Средства успешно внесены. Транзакция отправлена: {tx_hash.hex()}", 'success')
        except Exception as e:
            flash(f"Ошибка внесения средств: {str(e)}", 'danger')
    return render_template('deposit.html')

@app.route('/getinfo')
def getinfo():
    if 'account' not in session:
        flash("Пожалуйста, войдите в аккаунт", 'danger')
        return redirect(url_for('login'))
    try:
        balance = contract.functions.getContractBalance().call()
        estates = contract.functions.getestates().call()
        ads = contract.functions.getads().call()
        account_balance = contract.functions.getAccountBalance().call({'from': session['account']})
        return render_template('getinfo.html', balance=balance, estates=estates, ads=ads, account_balance=account_balance)
    except Exception as e:
        flash(f"Ошибка получения информации: {str(e)}", 'danger')
        return redirect(url_for('menu'))

@app.route('/logout')
def logout():
    session.pop('account', None)
    flash("Вы вышли из аккаунта", 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
