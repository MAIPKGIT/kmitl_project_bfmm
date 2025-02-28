import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment.development';
import { map } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class OrderingService {

  constructor(private http: HttpClient) { }

  getAllMenuTypes(){
    let getUrl = `${environment.serviceUrl}/api/menutype/`;
    return this.http.get<any>(getUrl);
  }

  getAllMenusById(id: any){
    let getUrl = `${environment.serviceUrl}/api/menu/type/${id}`;
    return this.http.get<any>(getUrl);
  }

  getCategoryById(id: any){
    let getUrl = `${environment.serviceUrl}/api/menutype/${id}`;
    return this.http.get<any>(getUrl);
  }

  verifyTableCode(code: string) {
    return this.http.get(`${environment.serviceUrl}/api/table/code/${code}`);
  }

  createOrder(orderData: any) {
    const postUrl = `${environment.serviceUrl}/api/order/`;
    return this.http.post(postUrl, orderData);
  }

  getOrderItemsByTable(tableId: number) {
    let getUrl = `${environment.serviceUrl}/api/order/get_orderitem_by_table/${tableId}`;
    return this.http.get<any>(getUrl);
  }
}
