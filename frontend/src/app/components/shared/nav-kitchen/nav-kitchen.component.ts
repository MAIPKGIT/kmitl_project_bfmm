import { Component, OnInit } from '@angular/core';
import Swal from 'sweetalert2';
import { Router } from '@angular/router';
import { NavgationService } from '../../../service/navgation.service';
import { TokenStorageService } from '../../../service/token-storage.service';

@Component({
  selector: 'app-nav-kitchen',
  standalone: false,
  
  templateUrl: './nav-kitchen.component.html',
  styleUrl: './nav-kitchen.component.css'
})
export class NavKitchenComponent implements OnInit{

  constructor(private service: NavgationService, private router: Router, private tokenStorage: TokenStorageService) { }

  isLoggedIn = false;

  ngOnInit(): void {

    this.isLoggedIn = !!this.tokenStorage.getToken();

  }

  logout(): void {
    this.tokenStorage.signOut();
    this.isLoggedIn = false;
    Swal.fire('Logged Out', 'You have been successfully logged out.', 'success');
    this.router.navigate(['/']);
  }

}
