import { Component, OnInit } from '@angular/core';
import { WasteService } from '../../../service/waste.service';

@Component({
  selector: 'app-waste',
  standalone: false,
  
  templateUrl: './waste.component.html',
  styleUrl: './waste.component.css'
})
export class WasteComponent implements OnInit{

  waste: any = [];
  selectedDate: string = '';
  totalPrice: number = 0;
  isDataEmpty: boolean = false; 

  constructor(private service: WasteService) { }
  ngOnInit(): void {
    const today = new Date();
    this.selectedDate = today.toISOString().split('T')[0];
    this.fetchWasteByDate(); 
  }

  fetchWasteByDate(): void {
    this.service.getWasteByDate(this.selectedDate).subscribe(
      (res) => {
        if (Array.isArray(res) && res.length > 0) { 
          this.waste = res;
          this.isDataEmpty = false;
          console.log('History on selected date:', this.waste);
          this.calculateTotalPrice();
        } else {
          this.waste = [];
          this.isDataEmpty = true;
          this.totalPrice = 0;
        }
      },
      (error) => {
        console.error('Error fetching waste by date:', error);
        this.waste = [];
        this.isDataEmpty = true; 
        this.totalPrice = 0;
      }
    );
  }

  calculateTotalPrice(): void {
    this.totalPrice = this.waste.reduce((sum: number, item: any) => {
      const price = parseFloat(item.price) || 0; 
      return sum + price;
    }, 0);
  
    console.log('Total Price:', this.totalPrice);
  }  
}
