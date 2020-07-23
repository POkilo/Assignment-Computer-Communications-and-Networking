import os
import string 
import socket
import threading as td
import multiprocessing as mp
import time
import re

server_socket_port = [50000,50001,50002,50003,50004]
client_socket_port = 50005 #[50005,50006,50007,50008,50009]   
HOST = '127.0.0.1'
turn = 0
flag = 0
done = [0,0,0,0,0]
N = 5
node_name = ['A','B','C','D','E']
result = ''
def dv_update(node,dv,data, adj):
	dv[data[0]] = data[1:]
	for i in range(N):
		if i!=node:
			dv[node][i] = min([(dv[node][data[0]]+ dv[data[0]][i]) ,dv[node][i]])
	return dv


def display_2Dmatrix(matrix):
	for index,i in enumerate(matrix):
		print '          ',node_name[index],i
	print '\n'
	return
def write_2Dmatrix(matrix,node):
	op = open('OUTPUT.txt','a')
	op.write('~~~~~~~Node'+node_name[node]+'~~~~~~~\n')
	for i in matrix:
		for j in i:
			op.write(str(j)+' ')
		op.write('\n')

def working(node, neighbor):
	dv_matrix = []
	last_dv_matrix = []
	adj = []
	node_num = len(neighbor)
	updated = 1
	count = 0
	old = -1
	for i in range(node_num):
		if i == node:
			dv_matrix.append(neighbor)
			for j in range(node_num):
				if neighbor[j] != 0 and neighbor[j] != 999:
					count += 1
					adj.append(j)	
		else:
			dv_matrix.append([999 for i in range(node_num)])
	
	sPORT = server_socket_port[node]
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.bind((HOST, sPORT))
	server.listen(1)	
	while 1:
		global turn, flag, done
		if done == [1,1,1,1,1] :
			break
		# ==========================================
		# if this neighbor is connected to this node
		# activate the server
		if  (turn%5 in adj)  and flag != 0 and turn != old:
			old = turn	
			# print '\nserver node', node , 'the flag is', flag , 'turn is', turn
			conn, addr = server.accept()
			data = conn.recv(1024)
			data = data.split(' ')
			data = map(int,data)
	
			#/////////////////////
			if data[0] == -1:
				flag -= 1
				continue
			#/////////////////////
			
			last_dv_matrix[:] = dv_matrix
			# print '\nmessage got at node ',node,':' ,data
			print '\nsending DV to node', node_name[node]
			print 'Node', node_name[node],'received DV from', node_name[int(data[0])]
			print 'Updating DV matrix at node', node_name[node]
			dv_matrix = dv_update(node,dv_matrix,data,adj)
			if dv_matrix != last_dv_matrix:
				updated = 1
			print 'New DV matrix at node',node_name[node],'\n'
			display_2Dmatrix(dv_matrix),'\n'
			flag -= 1
		# ==========================================
		# if it is this nodes turn
		# activate the client 
		# sleep 1 sec for all nodes to update dv
		elif turn%5 == node and flag == 0 : 
			print '==============================='
			print 'Round', turn+1, ':', node_name[node]
			print 'Current DV matrix =' 
			display_2Dmatrix(dv_matrix)
			print 'Last DV matrix =' 
			display_2Dmatrix(last_dv_matrix)
			if updated:
				print 'Updated from last DV matrix or the same? Updated\n'
			else:
				print 'Updated from last DV matrix or the same? Remain the same\n'
		
			flag += count  
			for index in adj:
				time.sleep(1)
				# notify the servers here
				# wait until the server is on
				cPORT = server_socket_port[index]
				client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				client.connect((HOST, cPORT))
				# ////////////////////
				
				if updated==0:
					client.sendall(str(-1))
					client.close()
					continue
				message = ''
				for i in dv_matrix[node]:
					message += (' '+str(i))
				client.sendall(str(node)+message)
				client.close()
			while flag!=0:
				continue	
			if updated==0:
				done[node] = 1
			turn+=1
			updated = 0
			last_dv_matrix[:] = dv_matrix
		else:
			time.sleep(2)
			continue
	server.close()
	print '\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
	print 'Final Node',node_name[node],'DV ='
	display_2Dmatrix(dv_matrix)
	write_2Dmatrix(dv_matrix,node)
	return 

def network_init():
	fi = raw_input('>type the txt to read:')
	open('OUTPUT.txt','w').write('')
	pattern =  re.compile('[0-9\t]+')
	network = re.findall(pattern,open(fi).read())
	network = [i.split('\t') for i in network]
	for index,i in enumerate(network):
		network[index]=map(int,network[index])
		for index2, j in enumerate(network[index]):
			if j==0 and index!=index2:
				network[index][index2] = 999
	print network
	
	nodes = []
	for i in range(len(network)):
		nodes.append(td.Thread(target = working,  args = (i, network[i],)  ))
	
	for i in range(len(network)):
		nodes[i].start()

	for i in range(len(network)):
		nodes[i].join()

	return



def main():
	network_init()
	print 'whole process ends'
	print 'Number of rounds till convergence (Round # when one of the nodes last updated its DV) =',turn
	return 	


if __name__ == '__main__':
	main() 