from flask import Flask
from flask import request
import requests
import redis
import json
from jobs import add_job,check_status


app = Flask(__name__)

def get_redis_client():
	"""
	Returns redis client object for use in flask app. Hard coded for TACC isp02 port 6379 and lew2547's unique host
	Args:
		none
	Returns:
		redis client object
	"""
	return redis.StrictRedis(host='10.108.182.250',port=6437)


@app.route('/',methods=['GET'])
def hello_world():
	return 'Hello World\n'

@app.route('/data',methods=['GET','POST'])
def data_route():
	"""
	The route has two functions. 
	For a POST request. The function updates the redis database thorugh a python redis server object. 
	For a GET request. The function returns the meteorite landind data loaded from the POST request.
	Args:
		none
	Returns
		if POST: confirmations string
		if GET: json of meteorite landing data 
	"""
	if request.method == 'POST':
		rd = get_redis_client()
		sl = requests.get("https://raw.githubusercontent.com/lukewilson37/coe332-MarsSoilSampleAnalysis/main/initial_sol_list.txt")
		sl_list = list(sl.content.decode('utf-8').split("\n"))
		sl_list.remove("")
		for sol in sl_list:
			sol_info_dict = {}
			sol_info = requests.get("https://"+sol)
			sol_info_list = list(sol_info.content.decode('utf-8').split("\r\n"))
			sol_info_list.remove("")
			for i in range(1,len(sol_info_list)):
				sol_info_list_i = sol_info_list[i].replace(" ","").split(",")
				sol_info_dict[sol_info_list_i[0]] = sol_info_list_i[1]
			rd.set(sol[69:77],json.dumps(sol_info_dict))
		return 'stored'
	else:
		rd = get_redis_client()
		sol_test = rd.get('sol00047')
		return sol_test

@app.route('/abundancies/<solname>',methods=['GET'])
def return_sol_data(solname):
	rd = get_redis_client()
	sol_data_raw = rd.get(solname)
	sol_data_json = json.loads(sol_data_raw)
	return sol_data_raw

@app.route('/set_sol_list',methods=['GET'])
def get_sol_list():
	rd = get_redis_client()
	keys_sol = []
	for sol_key in rd.keys(pattern="sol*"):
		keys_sol.append(sol_key.decode('utf-8'))
	rd.set('keys_sol',json.dumps({'keys_sol':keys_sol}))
	return "developing\n"	

@app.route('/jobs/results/<id>', methods=['GET'])
def job_results(id):
    """
    application route to return the results of a completed job.
    :param id:
    :return: histogram image produced by the worker
    """
    rd = get_redis_client()
    path = f'/app/{id}.png'
    with open(path, 'wb') as f:
        f.write(rd.hget(str(id), 'image'))
    return send_file(path, mimetype='image/png', as_attachment=True)

@app.route('/jobs/<substance>', methods=['POST'])
def job_creator(substance):
    """
    application route to create new job. This route accepts a substance input by the user in the URL
    :param: substance
    """
    #add_job(substance)
    return add_job(substance)

<<<<<<< HEAD
@app.route('/delete/<sol>',methods=['POST'])
def delete_sol_route(sol):
	"""
	application route to delete a key.
	arguments: key value (str)
	return: success or failure (str)
	"""
	if not rd.get(sol):
		return "key does not exist\n"
	rd.remove(sol)
	return "key successfully removed\n"
=======
@app.route('/jobs/status/<job_id>',methods=['GET'])
def check_status_route(job_id):
	"""
	application route to check job status
	arguments: job id (string)
	returns: status (string)
	"""
	return check_status(job_id)
>>>>>>> 2a8e9d60eb8bb02b4d130faefeb5a983f35a8762

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')
	

