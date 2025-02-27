import { TableStatusComponent } from './../pages/table-status/table-status.component';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormControl, FormGroup } from '@angular/forms';
import { ChangeDetectorRef } from '@angular/core';
import { OrderingService } from '../../service/ordering.service';
import Swal from 'sweetalert2';
import { TokenStorageService } from '../../service/token-storage.service';
import { TableStatusService } from '../../service/table-status.service';

@Component({
  selector: 'app-ordering',
  standalone: false,
  
  templateUrl: './ordering.component.html',
  styleUrl: './ordering.component.css'
})
export class OrderingComponent implements OnInit{
  menu_types: any;
  isLoggedIn = false;
  id: any;
  code: any;
  menu_by_type_id: any;
  category: any;
  menu_modalForm!: FormGroup;
  cartItems: any[] = [];
  number: number = 0;
  user: any;
  table: any;
  tableByCode: any;
  tableCode: any;

  constructor(private router: Router, private route: ActivatedRoute, private service_order: OrderingService, private cdr: ChangeDetectorRef, private tokenStorage: TokenStorageService,
    private tableService : TableStatusService)
  { 
    this.menu_modalForm = new FormGroup({
      id: new FormControl(null),
      image: new FormControl(),
      name: new FormControl(),
      des: new FormControl(),
      price: new FormControl(),
      qty: new FormControl(1), 
      note: new FormControl(''), 
    });    
  }

  ngOnInit(): void {
    this.service_order.getAllMenuTypes().subscribe((res) => {
      this.menu_types = res;
      console.log(this.menu_types);
    });

    // ตรวจสอบว่ามี Token หรือไม่
    this.isLoggedIn = !!this.tokenStorage.getToken();
    // this.user = localStorage.getItem('selectedTableId');
    // ดึงค่า code จาก URL
    this.code = this.route.snapshot.paramMap.get('code');
    console.log('QR Code:', this.code);

    if (this.code) {
      // ถ้ามี code ให้ตรวจสอบสถานะโต๊ะ
      this.verifyTableCode();
    }

    this.tableService.getTableByCode(this.code).subscribe((res)=>{
      this.table = res
      this.tableByCode = res.table_id
      this.tableCode = res.code

      console.log("asdfjasdf;lsajfl;");
      console.log("Table ID : ",this.tableByCode)
      console.log("Table Code : ", this.tableCode);
    })

    this.loadCartFromLocalStorage();
    this.id = this.route.snapshot.paramMap.get('id')
    
    this.service_order.getAllMenusById(this.id).subscribe((res)=>{
      this.menu_by_type_id = res
      console.log(this.menu_by_type_id);
    })

    this.service_order.getCategoryById(this.id).subscribe((res)=>{
      this.category = res
      console.log(this.category);
    })
  }

  verifyTableCode() {
    this.service_order.verifyTableCode(this.code).subscribe(
      (response) => {
        console.log('QR Code Verified:', response);
      },
      (error) => {
        Swal.fire('ข้อผิดพลาด', 'รหัส QR ไม่ถูกต้องหรือโต๊ะถูกปิดใช้งาน', 'error').then((err) => {
          console.log(err)
          this.router.navigate(['/']);
        });
      }
    );
  }

  selectMenuTypesById(id: any) {
      if (this.tableByCode && this.tableCode) {
        let url = `/ordering/${id}/${this.tableCode}`;
        console.log('Navigating to:', url);
    
        this.router.navigateByUrl('/', { skipLocationChange: true }).then(() => {
          this.router.navigate([url]);
        });
      } else {
        Swal.fire('ข้อผิดพลาด', 'ไม่พบ QR Code ของโต๊ะ!', 'error');
      }
    }  

  sendMenuToCart(menu:any): void {
    this.menu_modalForm.controls['id'].setValue(menu.id);
    this.menu_modalForm.controls['image'].setValue(menu.image);
    this.menu_modalForm.controls['name'].setValue(menu.name);
    this.menu_modalForm.controls['des'].setValue(menu.des);
    this.menu_modalForm.controls['price'].setValue(menu.price);
    this.menu_modalForm.controls['qty'].setValue(1);
    this.menu_modalForm.controls['note'].setValue(''); 
    console.log(menu)
  }

  addToCart(): void {
    const cartItem = {
      id: this.menu_modalForm.value.id,
      image: this.menu_modalForm.value.image,
      name: this.menu_modalForm.value.name,
      price: this.menu_modalForm.value.price,
      qty: this.menu_modalForm.value.qty || 1,
      note: (document.getElementById('menuNote') as HTMLTextAreaElement).value, // ดึงค่าจาก textarea
    };
  
    // ตรวจสอบว่ามีรายการในตะกร้าอยู่แล้วหรือไม่
    const existingItem = this.cartItems.find(
      (item) => item.id === cartItem.id && item.note === cartItem.note
    );
    if (existingItem) {
      existingItem.qty += cartItem.qty; // เพิ่มจำนวนในรายการเดิม
    } else {
      this.cartItems.push(cartItem); // เพิ่มรายการใหม่
    }
    Swal.fire('เพิ่มเมนูในตะกร้าแล้ว', 'Add Menu Seccess!', 'success');
  
    // บันทึกข้อมูลตะกร้าใน Local Storage
    this.saveCartToLocalStorage();
  
    // แสดงข้อมูลใน Console
    console.log('เพิ่มสินค้าในตะกร้า:', cartItem);
    console.log('รายการทั้งหมดในตะกร้า:', this.cartItems);

    this.cdr.detectChanges();
  }  

  increaseQty(index: number): void {
    const currentQty = this.menu_modalForm.value.qty || 1;
    this.menu_modalForm.controls['qty'].setValue(currentQty + 1);
    // แสดงข้อมูลใน console
    console.log('เพิ่มจำนวนสินค้าในตะกร้า:', this.cartItems[index]);
    console.log('รายการทั้งหมดในตะกร้า:', this.cartItems);
  }

  decreaseQty(index: number): void {
    const currentQty = this.menu_modalForm.value.qty || 1;
    if (currentQty > 1) {
      this.menu_modalForm.controls['qty'].setValue(currentQty - 1);
    }
    // แสดงข้อมูลใน console
    console.log('ลดจำนวนสินค้าในตะกร้า:', this.cartItems[index]);
    console.log('รายการทั้งหมดในตะกร้า:', this.cartItems);
  }

  getTotalPrice(): number {
    return this.cartItems.reduce(
      (total, item) => total + item.price * item.qty,
      0
    );
  }

  saveCartToLocalStorage(): void {
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('cartItems', JSON.stringify(this.cartItems));
    } else {
      console.warn('localStorage is not available. Data will not be saved.');
    }
  }  

  loadCartFromLocalStorage(): void {
    if (typeof localStorage !== 'undefined') {
      const storedCart = localStorage.getItem('cartItems');
      if (storedCart) {
        this.cartItems = JSON.parse(storedCart);
        console.log('โหลดข้อมูลตะกร้าจาก Local Storage:', this.cartItems);
      }
    } else {
      console.warn('localStorage is not available.');
    }
  }  

  removeFromCart(index: number): void {
    this.cartItems.splice(index, 1);
    this.saveCartToLocalStorage();
    console.log('ลบสินค้าออกจากตะกร้า:', index);
    console.log(localStorage);
  }

  confirmOrder(): void {
    if (this.cartItems.length === 0) {
      Swal.fire('ข้อผิดพลาด', 'กรุณาเพิ่มรายการสินค้าลงในตะกร้า!', 'error');
      return;
    }
  
    // ดึงข้อมูลจาก localStorage และ URL
    const tableId = this.tableByCode;
    const code = this.code; // ดึง code จาก URL ที่ได้รับมา
  
    if (!tableId || !code) {
      Swal.fire('ข้อผิดพลาด', 'ไม่พบข้อมูลโต๊ะหรือ QR Code!', 'error');
      return;
    }
  
    const orderItems = this.cartItems.map(item => {
      return {
        id: item.id,
        qty: item.qty,
        note: item.note?.trim() || 'ไม่มี' // ถ้าไม่มีหมายเหตุให้กำหนดเป็น 'ไม่มี'
      };
    });
  
    const orderData = {
      code: code,  // รหัส QR ที่ดึงมาจาก URL
      people: "2", // จำนวนลูกค้า (สามารถเปลี่ยนได้หากมีข้อมูลจากฟอร์ม)
      table: Number(this.tableByCode),
      items: orderItems,
      total_price: this.getTotalPrice(), // คำนวณราคารวม
    };
  
    console.log('ข้อมูลการสั่งซื้อที่ส่งไป API:', JSON.stringify(orderData, null, 2));
  
    this.service_order.createOrder(orderData).subscribe(
      (response) => {
        Swal.fire('ยืนยันคำสั่งเรียบร้อย', 'Your order has been placed successfully!', 'success');
        this.cartItems = []; // ล้างตะกร้าหลังจากสั่งสำเร็จ
        this.saveCartToLocalStorage(); // อัปเดต localStorage หลังล้างตะกร้า
      },
      (error) => {
        console.error('Error placing order:', error);
        Swal.fire('ข้อผิดพลาด', error.error.message || 'ไม่สามารถสั่งซื้อได้!', 'error');
      }
    );
  }
  
}