from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import PeopleSerializer,ColorSerializer, RegisterSerializer, LoginSerializer
from .models import Person
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound
from rest_framework import viewsets
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.core.paginator import Paginator
from rest_framework.decorators import action

from rest_framework.decorators import action

from django.contrib.auth.models import User
# Create your views here.


class LoginAPI(APIView):
	def post(self,request):
		data = request.data
		serializer = LoginSerializer(data=data)
		if not serializer.is_valid():
			return Response({'status': False, 'message':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
		user = authenticate(username=serializer.data['username'],password=serializer.data['password'])
		if not user:
			return Response({'status': False, 'message':'invalid credentials'},status=status.HTTP_400_BAD_REQUEST)
		token, _ = Token.objects.get_or_create(user=user)
		return Response({'status':True,'message':'user authentication succcessful', 'token': str(token)},status=status.HTTP_201_CREATED)

class RegisterAPI(APIView):
	def post(self,request):
		data = request.data
		serializer = RegisterSerializer(data=data)
		if not serializer.is_valid():
			return Response({'status': False, 'message':serializer.errors},status=status.HTTP_400_BAD_REQUEST)
		serializer.save()

		return Response({'status':True,'message':'user created'},status=status.HTTP_201_CREATED)






class PeopleViewSet(viewsets.ModelViewSet):
	serializer_class = PeopleSerializer
	queryset = Person.objects.all()


	def get_object(self, pk):
		# try to get the person instance by pk
		try:
			person = Person.objects.get(pk=pk)
		# if it does not exist, raise a NotFound exception
		except Person.DoesNotExist:
			raise NotFound(detail="Person not found")
		# return the person instance
		return person
	def update(self, request, pk=None):
		person = self.get_object(pk=pk)
		serializer = PeopleSerializer(person, data=request.data)
		# validate the data
		serializer.is_valid(raise_exception=True)
		# pop the color data from the validated data
		color_data = serializer.validated_data.pop('color', None)
		# update the color instance if present
		if color_data is not None:

			color_serializer = ColorSerializer(person.color, data=color_data)
			color_serializer.is_valid(raise_exception=True)
			color_serializer.save()
			person.color = color_serializer.instance
			person.save(update_fields=['color'])

		# save the person instance with the remaining validated data
		serializer.save()
		# return the updated person data
		return Response(serializer.data)

	@action(detail=True, methods=['POST'])
	def send_email(self, request,pk):
		obj = Person.objects.get(pk=pk)
		serializer = PeopleSerializer(obj)
		return Response({

			'status': True,
			'message': 'action done succesfully',
			'data': serializer.data

		})



class PersonAPI(APIView):
	permission_classes = [IsAuthenticated]
	authentication_classes = [TokenAuthentication]
	def get(self,request):
		try:

			objs = Person.objects.all()
			page = request.GET.get('page',1)
			page_size = 2
			paginator = Paginator(objs,page_size)
			serializer = PeopleSerializer(paginator.page(page), many=True)
			return Response(serializer.data)
		except Exception as e:
			return Response({
				'status': False,
				'message': 'Invalid page number'
			})
	def post(self, request):
		data = request.data
		serializer = PeopleSerializer(data=data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors)

	def get_object(self, pk):
		# try to get the person instance by pk
		try:
			person = Person.objects.get(pk=pk)
		# if it does not exist, raise a NotFound exception
		except Person.DoesNotExist:
			raise NotFound(detail="Person not found")
		# return the person instance
		return person
	def put(self,request):
		person = self.get_object(pk=request.data['id'])

		serializer = PeopleSerializer(person, data=request.data)
		# validate the data
		serializer.is_valid(raise_exception=True)
		# pop the color data from the validated data
		color_data = serializer.validated_data.pop('color', None)
		# update the color instance if present
		if color_data is not None:
			color_serializer = ColorSerializer(person.color, data=color_data)
			color_serializer.is_valid(raise_exception=True)
			color_serializer.save()
		# save the person instance with the remaining validated data
		serializer.save()
		# return the updated person data
		return Response(serializer.data)


	def patch(self, request, pk=None):
		# get the person instance by pk
		person = self.get_object(pk=request.data['id'])
		# create a serializer with the partial data and the instance
		serializer = PeopleSerializer(person, data=request.data, partial=True)
		# validate the data
		serializer.is_valid(raise_exception=True)
		# pop the color data from the validated data
		color_data = serializer.validated_data.pop('color', None)
		# update the color instance if present
		if color_data is not None:
			color_serializer = ColorSerializer(person.color, data=color_data, partial=True)
			color_serializer.is_valid(raise_exception=True)
			color_serializer.save()
		# save the person instance with the remaining validated data
		serializer.save()
		# return the updated person data
		return Response(serializer.data)

	def delete(self,request):
		data = request.data
		obj = Person.objects.get(id=data['id'])
		obj.delete()
		return Response({'message':'item deleted'})



@api_view(['GET'])  # pass the methods that you required as a list
def index(request):
	if request.method=='GET':
		objs = Person.objects.all()
		serializer = PeopleSerializer(objs, many=True)
		return Response(serializer.data)
@api_view(['GET','POST','PUT','PATCH','DELETE'])
def people(request):
	if request.method == 'GET':
		#if request.data['id']:
			#data = request.data
			#obj = Person.objects.get(id=data['id'])
			#serializer = PeopleSerializer(obj)
			#return Response(serializer.data)
		#else:
		#objs = Person.objects.all()
		objs = Person.objects.filter(color__isnull=False)
		serializer = PeopleSerializer(objs, many=True)
		return Response(serializer.data)
	elif request.method == 'POST':
		data = request.data
		serializer = PeopleSerializer(data=data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors)
	elif request.method == 'PUT':
		data=request.data
		serializer=PeopleSerializer(data=data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors)
	elif request.method == 'PATCH':
		data=request.data
		obj = Person.objects.get(id=data['id'])
		serializer=PeopleSerializer(obj, data=data, partial=True)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors)
	elif request.method == 'DELETE':
		data = request.data
		obj = Person.objects.get(id=data['id'])
		obj.delete()
		return Response({'message': 'person deleted'})