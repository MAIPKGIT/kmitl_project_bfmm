import { Component, OnInit } from '@angular/core';
import Swal from 'sweetalert2';
import { Router } from '@angular/router';
import { NavgationService } from '../../../service/navgation.service';
import { TokenStorageService } from '../../../service/token-storage.service';

@Component({
  selector: 'app-navbar',
  standalone: false,

  templateUrl: './navgation.component.html',
  styleUrl: './navgation.component.css'
})
export class NavgationComponent implements OnInit {

  menu_types: any;
  isLoggedIn = false;

  constructor(private service: NavgationService, private router: Router, private tokenStorage: TokenStorageService) { }

  ngOnInit(): void {
    this.service.getAllMenuTypes().subscribe((res) => {
      this.menu_types = res;
      console.log(this.menu_types);
    });

    // ตรวจสอบว่ามี Token หรือไม่
    this.isLoggedIn = !!this.tokenStorage.getToken();
  }

  selectMenuTypesById(id: any) {
    const tableId = localStorage.getItem('selectedTableId'); 
    const qrCode = localStorage.getItem(`table_qr_${tableId}`);
    console.log(tableId)
    console.log(qrCode)
  
    if (tableId && qrCode) {
      let url = `/ordering/${id}/${qrCode}`;
      console.log('Navigating to:', url);
  
      this.router.navigateByUrl('/', { skipLocationChange: true }).then(() => {
        this.router.navigate([url]);
      });
    } else {
      Swal.fire('ข้อผิดพลาด', 'ไม่พบ QR Code ของโต๊ะ!', 'error');
    }
  }  

  logout(): void {
    this.tokenStorage.signOut();
    this.isLoggedIn = false;
    Swal.fire('Logged Out', 'You have been successfully logged out.', 'success');
    this.router.navigate(['/']);
  }

}
