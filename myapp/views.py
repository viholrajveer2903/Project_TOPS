from django.shortcuts import render,redirect
from .models import User,Product,Wishlist,Cart,Transaction
from django.conf import settings
from .paytm import generate_checksum, verify_checksum
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
import random

# Create your views here.

def initiate_payment(request):
    user=User.objects.get(email=request.session['email'])
    try:
        amount = int(request.POST['amount'])
    except Exception as e:
    	print(e)
    	return render(request, 'cart.html', context={'error': 'Wrong Accound Details or amount'})																		
    

    transaction = Transaction.objects.create(made_by=user, amount=amount)	
    transaction.save()
    merchant_key = settings.PAYTM_SECRET_KEY
    params = (
        ('MID', settings.PAYTM_MERCHANT_ID),
        ('ORDER_ID', str(transaction.order_id)),
        ('CUST_ID', str(transaction.made_by.email)),
        ('TXN_AMOUNT', str(transaction.amount)),
        ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
        ('WEBSITE', settings.PAYTM_WEBSITE),
        # ('EMAIL', request.user.email),
        # ('MOBILE_N0', '9911223388'),
        ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
        ('CALLBACK_URL', 'http://localhost:8000/callback/'),
        # ('PAYMENT_MODE_ONLY', 'NO'),
    )

    paytm_params = dict(params)
    checksum = generate_checksum(paytm_params, merchant_key)

    transaction.checksum = checksum
    transaction.save()

    paytm_params['CHECKSUMHASH'] = checksum
    print('SENT: ', checksum)
    return render(request, 'redirect.html', context=paytm_params)

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        received_data = dict(request.POST)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                paytm_checksum = value[0]
            else:
                paytm_params[key] = str(value[0])
        # Verify checksum
        is_valid_checksum = verify_checksum(paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
        if is_valid_checksum:
            received_data['message'] = "Checksum Matched"
        else:
            received_data['message'] = "Checksum Mismatched"
            return render(request, 'callback.html', context=received_data)
        return render(request, 'callback.html', context=received_data)


def index(request):
	try:
		user=User.objects.get(email=request.session['email'])
		print(user.usertype)
		if user.usertype=="buyer":
			return render(request,'index.html')
		else:
			return render(request,'seller-index.html')
	except Exception as e:
		print(e)
		return render(request,'index.html')
		
def seller_index(request):
	return render(request,'seller-index.html')

def shop(request):
	products=Product.objects.all()
	products500=Product.objects.filter(product_price__range=(0,500))
	products1000=Product.objects.filter(product_price__range=(501,1000))
	products10000=Product.objects.filter(product_price__range=(1001,10000))
	return render(request,'shop.html',{'products':products,'products500':products500,'products1000':products1000, 'products10000':products10000})

def products500(request):
	print(request.POST['productrange'])
	products=Product.objects.filter(product_price__range=(0,500))
	print("Products: ",products)
	products500=Product.objects.filter(product_price__range=(0,500))
	products1000=Product.objects.filter(product_price__range=(501,1000))
	products10000=Product.objects.filter(product_price__range=(1001,10000))
	return render(request,'shop.html',{'products':products,'products500':products500,'products1000':products1000, 'products10000':products10000})

def products1000(request):
	print(request.POST['productrange'])
	products=Product.objects.filter(product_price__range=(501,1000))
	print("Products: ",products)
	products500=Product.objects.filter(product_price__range=(0,500))
	products1000=Product.objects.filter(product_price__range=(501,1000))
	products10000=Product.objects.filter(product_price__range=(1001,10000))
	return render(request,'shop.html',{'products':products,'products500':products500,'products1000':products1000, 'products10000':products10000})

def products1001(request):
	print(request.POST['productrange'])
	products=Product.objects.filter(product_price__range=(1001,10000))
	print("Products: ",products)
	products500=Product.objects.filter(product_price__range=(0,500))
	products1000=Product.objects.filter(product_price__range=(501,1000))
	products10000=Product.objects.filter(product_price__range=(1001,10000))
	return render(request,'shop.html',{'products':products,'products500':products500,'products1000':products1000, 'products10000':products10000})

def detail(request,pk):
	wishlist_flag=False	
	cart_flag=False
	path=request.get_full_path()
	product=Product.objects.get(pk=pk)
	try:
		user=User.objects.get(email=request.session['email'])
		Wishlist.objects.get(user=user,product=product)
		wishlist_flag=True
	except:
		pass
	try:
		user=User.objects.get(email=request.session['email'])
		Cart.objects.get(user=user,product=product)
		cart_flag=True
	except:
		pass
	return render(request,'detail.html',{'product':product,'path':path,'wishlist_flag':wishlist_flag,'cart_flag':cart_flag,})

def checkout(request):
	return render(request,'checkout.html')

def contact(request):
	return render(request,'contact.html')

def login(request):
	if request.method=="POST":
		path=request.POST['path']
		print("Path : ",path)
		try:
			user=User.objects.get(email=request.POST['email'])
			if user.password==request.POST['password']:
				if user.usertype=="buyer":
					request.session['fname']=user.fname 
					request.session['email']=user.email
					request.session['profile_pic']=user.profile_pic.url 
					wishlists=Wishlist.objects.filter(user=user)
					request.session['wishlist_count']=len(wishlists)
					carts=Cart.objects.filter(user=user)
					request.session['cart_count']=len(carts)
					if path==None:
						return redirect(path)
					else:
						return render(request,'index.html')
						
					
				else:
					request.session['fname']=user.fname 
					request.session['email']=user.email
					request.session['profile_pic']=user.profile_pic.url 
					return render(request,'seller-index.html')
			else: 
				msg="Incorrect Password"
				return render(request,'login.html',{'msg':msg})
		except Exception as e:
			print(e)
			msg="Email Not Registerd"
			return render(request,'login.html',{'msg':msg})
	else:
		try:
			user=User.objects.get(email=request.session['email'])
			print(user.usertype)
			if user.usertype=="buyer":
				return render(request,'index.html')
			else:
				return render(request,'seller-index.html')
		except Exception as e:
			path=request.GET.get('path')
			return render(request,'login.html',{'path':path})

def register(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			msg="Email Already Registerd"
			return render(request,'register.html',{'msg':msg})
		except:
			if request.POST['password']==request.POST['cpassword']:
				User.objects.create(
						usertype=request.POST['usertype'],
						fname=request.POST['fname'],
						lname=request.POST['lname'],
						email=request.POST['email'],
						mobile=request.POST['mobile'],
						address=request.POST['address'],
						password=request.POST['password'],
						profile_pic=request.FILES['profile_pic'],
					)
				msg="User Registerd Successfully"
				return render(request,'login.html',{'msg':msg})
			else:
				msg="Password & Confirm Password Does Not Matched"
				return render(request,'register.html',{'msg':msg})
	else:
		return render(request,'register.html')

def logout(request):
	try:
		del request.session['email']
		del request.session['fname']
		del request.session['profile_pic']
		del request.session['wishlist_count']
		del request.session['cart_count']
		msg="User Logged Out"
		return render(request,'login.html',{'msg':msg})
	except:
		return render(request,'login.html')

def change_password(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.session['email'])
			if user.password==request.POST['old_password']:
				if request.POST['new_password']==request.POST['cnew_password']:
					user.password=request.POST['new_password']
					user.save()
					return redirect('logout')
				else:
					msg="New Password & Confirm New Password Does Not Matched"
					return render(request,'change-password.html',{'msg':msg}) 
			else:
				msg="Old Password Does Not Matched"
				return render(request,'change-password.html',{'msg':msg})
		except Exception as e:
			print(e)
			msg="Password dose not match"
			return render(request,'change-password.html') 
	else:
		return render(request,'change-password.html')  

def forgot_password(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			otp=random.randint(1000,9999)
			subject = 'OTP For Forgot Password'
			message = 'Hello USer, Your OTP For Forgot Password Is : '+str(otp)
			email_from = settings.EMAIL_HOST_USER
			recipient_list = [user.email,]
			send_mail( subject, message, email_from, recipient_list )
			return render(request,'otp.html',{'email':user.email,'otp':otp})

		except Exception as e:
			print(e)
			msg="Email Not Resgistered"
			return render(request,'forgot-password.html',{'msg':msg})


	else:
		return render(request,'forgot-password.html')

def verify_otp(request):
	email=request.POST['email']
	otp=request.POST['otp']
	uotp=request.POST['uotp']
	if otp==uotp:
		return render(request,'new_password.html',{'email':email})
	else:
		msg="Invalid OTP"
		return render(request,'otp.html',{'email':email,'otp':otp,'msg':msg})

def new_password(request):
	email=request.POST['email']
	np=request.POST['new_password']
	cnp=request.POST['cnew_password']

	if np==cnp:
		user=User.objects.get(email=email)
		User.password=np
		user.save()
		msg="Password Updated Successfully"
		return render(request,'login.html',{'msg':msg})

	else:
		msg='New Password & Confirm New Password Does Not Matched'
		return render(request,'new_password.html',{'email':email,'msg':msg})

def profile(request):
	user=User.objects.get(email=request.session['email'])
	if request.method=="POST":
		user.fname=request.POST['fname']
		user.lname=request.POST['lname']
		user.mobile=request.POST['mobile']
		user.address=request.POST['address']
		user.gender=request.POST['gender']
		user.fname=request.POST['fname']
		try:
			user.profile_pic=request.FILES['profile_pic']
		except:
			pass
		user.save()
		request.session['profile_pic']=user.profile_pic.url
		msg="Profile Updated Successfully "
		return render(request,'profile.html',{'user':user,'msg':msg})
	else:
		return render(request,'profile.html',{'user':user})

def seller_change_password(request):
	if request.method=="POST":
		user=User.objects.get(email=request.session['email'])
		if user.password==request.POST['old_password']:
			if request.POST['new_password']==request.POST['cnew_password']:
				user.password=request.POST['new_password']
				user.save()
				return redirect('logout')
			else:
				msg="New Password & Confirm New Password Does Not Matched"
				return render(request,'seller-change-password.html',{'msg':msg}) 
		else:
			msg="Old Password Does Not Matched"
			return render(request,'seller-change-password.html',{'msg':msg}) 
	else:
		return render(request,'seller-change-password.html')  

def seller_add_product(request):
	seller=User.objects.get(email=request.session['email'])
	if request.method=="POST":
		Product.objects.create(
				seller=seller,
				product_category=request.POST['product_category'],
				product_name=request.POST['product_name'],
				product_price=request.POST['product_price'],
				product_desc=request.POST['product_desc'],
				product_size=request.POST['product_size'],
				product_image=request.FILES['product_image']
			)
		msg="Product Added Successfully"
		return render(request,'seller-add-product.html',{'msg':msg})

	else:
		return render(request,'seller-add-product.html')

def seller_view_product(request):
	seller=User.objects.get(email=request.session['email'])
	products=Product.objects.filter(seller=seller)
	return render(request,'seller-view-product.html',{'products':products})

def seller_product_detail(request,pk):
	product=Product.objects.get(pk=pk)
	return render(request,'seller_product_detail.html',{'product':product})

def seller_edit_product(request,pk):
	product=Product.objects.get(pk=pk)
	if request.method=="POST":
		product.product_category=request.POST["product_category"]
		product.product_name=request.POST["product_name"]
		product.product_price=request.POST["product_price"]
		product.product_desc=request.POST["product_desc"]
		product.product_size=request.POST["product_size"]
		try:
			product.product_image=request.FILES['product_image']
		except:
			pass
		product.save()
		msg="Product Updated Successfully"
		return render(request,'seller-edit-product.html',{'product':product,'msg':msg})
	else:
		return render(request,'seller-edit-product.html',{'product':product})

def seller_delete_product(request,pk):
	product=Product.objects.get(pk=pk)
	product.delete()
	return redirect('seller-view-product')

def wishlist(request):
	user=User.objects.get(email=request.session['email'])
	wishlist=Wishlist.objects.filter(user=user)
	request.session['wishlist_count']=len(wishlist)
	return render(request,'wishlist.html',{'wishlist':wishlist})

def add_to_wishlist(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Wishlist.objects.create(user=user,product=product)
	return redirect('wishlist')

def remove_from_wishlist(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	wishlist=Wishlist.objects.get(user=user,product=product)
	wishlist.delete()
	return redirect('wishlist')

def cart(request):
	net_price=0
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user)
	for i in carts:
		net_price=net_price+i.total_price
	request.session['cart_count']=len(carts)
	return render(request,'cart.html',{'carts':carts,'net_price':net_price})

def add_to_cart(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Cart.objects.create(user=user,product=product,product_price=product.product_price,product_qty=1,total_price=product.product_price)
	return redirect('cart')

def remove_from_cart(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	cart=Cart.objects.get(user=user,product=product)
	cart.delete()
	return redirect('cart')

def change_qty(request):
	cid=int(request.POST['cid'])
	cart=Cart.objects.get(pk=cid)
	product_price=cart.product.product_price
	product_qty=int(request.POST['product_qty'])
	total_price=product_price*product_qty
	cart.product_qty=product_qty
	cart.total_price=total_price
	cart.save()
	return redirect('cart')

def shop_detail(request):
	return render(request,'shop-detail.html')

def search(request):
	search=request.POST['search']
	product=Product.objects.filter(product_name__contains=search)
	return render(request,'search.html',{'products':product})

