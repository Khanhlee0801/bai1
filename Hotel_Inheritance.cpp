#include <iostream>
using namespace std;
class phongthuong
{
private:
protected:
public:
	void mota()
	{
		cout << "\ngia tien la 500.000";
	}
};
class phongdoi
{
private:
protected:
public:
	void mota()
	{
		cout << "\ngia tien la 1.000.000 ";
	}
};
class phongvip
{
private:
protected:
public:
	void mota()
	{
		cout << "\n gia tien la 5.000.000";
	}
};
class khachsan
{
private:
	phongthuong thuong[5];
	phongdoi doi[3];
	phongvip vip[2];
protected:
public:
	void menu()
	{
		for (int i = 0; i < 5; i++) thuong[i].mota();
		for (int i = 0; i < 3; i++) doi[i].mota();
		for (int i = 0; i < 2; i++) vip[i].mota();
	}
};
int main()
{
	khachsan vuive;
	vuive.menu();
}