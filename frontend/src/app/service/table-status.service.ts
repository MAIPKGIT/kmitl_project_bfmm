import { Injectable} from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../environments/environment.development';
import { TokenStorageService } from './token-storage.service';
@Injectable({
  providedIn: 'root'
})
export class TableStatusService {
  constructor(private http: HttpClient, private tokenStorage: TokenStorageService) {}

  getAllTable(){
    let getUrl = `${environment.serviceUrl}/api/table/`;
    return this.http.get<any>(getUrl);
  }

  getAllPayment() {
    let getUrl = `${environment.serviceUrl}/api/payment/`;
    return this.http.get<any>(getUrl);
  }

  getAllOrder() {
    let getUrl = `${environment.serviceUrl}/api/order/`;
    return this.http.get<any>(getUrl);
  }

  getTableByCode(code: any) {
    let getUrl = `${environment.serviceUrl}/api/table/code/${code}`;
    return this.http.get<any>(getUrl);
  }

  getTableById(tableId: number) {
    let getUrl = `${environment.serviceUrl}/api/table/${tableId}`;
    return this.http.get<any>(getUrl);
  }

  updateTableStatus(table: any) {
    const payload = {
      table: table.table_id,
      people: table.people,
      status: table.status
    };
    console.log('Sending payload:', payload);
    return this.http.post(`${environment.serviceUrl}/api/table/status`, payload);
  }

  getPaymentTotalByTable(tableId: number) {
    const url = `${environment.serviceUrl}/api/payment/table/${tableId}`;
    return this.http.get<any>(url);
  }
  
  makePayment(paymentId: number, paymentMethod: string) {
    const payload = { payment_id: paymentId, payment_method: paymentMethod };
    console.log("ส่งข้อมูลไปที่ Backend:", payload);
  
    return this.http.post(`${environment.serviceUrl}/api/payment/make_payment`, payload);
  }
}
