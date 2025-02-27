import { Component, OnInit } from '@angular/core';
import { WasteService } from '../../../service/waste.service';

@Component({
  selector: 'app-waste',
  standalone: false,
  
  templateUrl: './waste.component.html',
  styleUrl: './waste.component.css'
})
export class WasteComponent implements OnInit{

  waste: any;
  selectedDate: string = '';

  constructor(private service: WasteService) { }
  ngOnInit(): void {
    const today = new Date();
    this.selectedDate = today.toISOString().split('T')[0];
    this.fetchWasteByDate(); 
  }

  fetchAllWaste(): void {
    this.service.getAllWaste().subscribe((res) => {
      this.waste = res;
      console.log('All Waste:', this.waste);
    });
  }

  fetchWasteByDate(): void {
    if (!this.selectedDate) {
      this.fetchAllWaste();
      return;
    }

    this.service.getWasteByDate(this.selectedDate).subscribe(
      (res) => {
        this.waste = res;
        console.log('Waste on selected date:', this.waste);
      },
      (error) => {
        console.error('Error fetching waste by date:', error);
        this.waste = [];
      }
    );
  }
}
