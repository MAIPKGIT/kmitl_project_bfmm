import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { Chart, ChartConfiguration, ChartOptions, ChartType, registerables } from 'chart.js';
import ChartDataLabels from 'chartjs-plugin-datalabels';
import { HistoryService } from '../../../service/history.service';

@Component({
  selector: 'app-history',
  standalone: false,
  
  templateUrl: './history.component.html',
  styleUrl: './history.component.css'
})
export class HistoryComponent implements OnInit{
  @ViewChild('salesChart', { static: true }) salesChart!: ElementRef;

  history: any[] = []; 
  selectedDate: string = '';
  totalPrice: number = 0;
  isDataEmpty: boolean = false; 

  chart!: Chart;

  constructor(private service: HistoryService) { 
    Chart.register(...registerables, ChartDataLabels);
  }
  ngOnInit(): void {
    const today = new Date();
    this.selectedDate = today.toISOString().split('T')[0];
    this.fetchHistoryByDate(); 
  }

  fetchHistoryByDate(): void {
    this.service.getHistoryByDate(this.selectedDate).subscribe(
      (res) => {
        if (Array.isArray(res) && res.length > 0) { 
          this.history = res;
          this.isDataEmpty = false;
          console.log('History on selected date:', this.history);
          this.calculateTotalPrice();
          this.updateChart();
        } else {
          this.history = [];
          this.isDataEmpty = true;
          this.totalPrice = 0;
          this.resetChart();
        }
      },
      (error) => {
        console.error('Error fetching history by date:', error);
        this.history = [];
        this.isDataEmpty = true; 
        this.totalPrice = 0;
        this.resetChart();
      }
    );
  }

  calculateTotalPrice(): void {
    this.totalPrice = this.history.reduce((sum: number, item: any) => {
      const total = parseFloat(item.total) || 0;
      return sum + total;
    }, 0);

    console.log('Total Price:', this.totalPrice);
  }

  updateChart(): void {
    const salesData: { [key: string]: { quantity: number; total: number } } = {};

    this.history.forEach((item) => {
      if (!salesData[item.menu_name]) {
        salesData[item.menu_name] = { quantity: 0, total: 0 };
      }
      salesData[item.menu_name].quantity += item.quantity;
      salesData[item.menu_name].total += item.total;
    });

    const labels = Object.keys(salesData);
    const quantities = labels.map((name) => salesData[name].quantity);
    const totals = labels.map((name) => salesData[name].total);

    if (this.chart) {
      this.chart.destroy();
    }

    this.chart = new Chart(this.salesChart.nativeElement, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'จำนวนที่ขาย',
            data: quantities,
            backgroundColor: 'rgb(111, 78, 55)',
            borderColor: 'rgba(111, 78, 55, 1)',
            borderWidth: 1
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          datalabels: {
            anchor: 'end',
            align: 'top',
            formatter: (value, context) => {  
              const index = context.dataIndex;
              return `฿${totals[index].toLocaleString()}`;
            },
            font: { weight: 'bold', size: 14 },
            color: '#000'
          }
        },
        scales: {
          y: { beginAtZero: true }
        }
      } as ChartOptions
    });
  }

  resetChart(): void {
    if (this.chart) {
      this.chart.destroy();
    }
  }
}
