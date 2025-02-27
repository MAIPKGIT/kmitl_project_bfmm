import { NavgationComponent } from './../../shared/navgation/navgation.component';
import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import Swal from 'sweetalert2'
import { Router } from '@angular/router';
import { ProductService } from '../../../service/product.service';

@Component({
  selector: 'app-product',
  standalone: false,
  
  templateUrl: './product.component.html',
  styleUrl: './product.component.css'
})
export class ProductComponent implements OnInit {
  products: any
  constructor(private service: ProductService){
    
  }
  ngOnInit(): void {
    
    this.service.getAllMenus().subscribe((res)=>{
      this.products = res
      console.log(this.products)
    })
  }

}
