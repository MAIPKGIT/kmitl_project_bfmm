import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment.development';

@Injectable({
  providedIn: 'root'
})
export class KitchenOrderService {
  constructor(private http: HttpClient) {}

  getAllMenuTypes() {
    let getUrl = `${environment.serviceUrl}/api/menutype/`;
    return this.http.get<any>(getUrl);
  }

  getAllNowOrders() {
    let getUrl = `${environment.serviceUrl}/api/order/get_all_now`;
    return this.http.get<any>(getUrl);
  }

  changeOrderStatus(payload: { order: number; order_item: number; operation: string }) {
    console.log("Calling API with payload:", payload);
    const url = `${environment.serviceUrl}/api/order/change_status_order`;
    return this.http.post(url, payload);
  }

  changeServeStatus(payload: { order: number; order_item: number; operation: string }) {
    console.log("Calling API with payload:", payload);
    const url = `${environment.serviceUrl}/api/order/change_status_serve`;
    return this.http.post(url, payload);
  }  

  getAllOrderItems() {
    let getUrl = `${environment.serviceUrl}/api/orderitem/`;
    return this.http.get<any>(getUrl);
  }

  cancelOrder(payload: { order: number; orderitem: number }) {
    console.log("Calling cancelOrder API with payload:", payload);
    const url = `${environment.serviceUrl}/api/order/cancel_order`;
    return this.http.post(url, payload);
  }
  
  wasteOrder(payload: { order_item_id: number; type: string; quantity: number; reason: string; note: string }) {
    console.log("Calling wasteOrder API with payload:", payload);
    const url = `${environment.serviceUrl}/api/order/waste_order`;
    return this.http.post(url, payload);
  }
  
  stockManager(payload: { menu_id: number; qty: number }) {
    const url = `${environment.serviceUrl}/api/order/stock_manager`;
    return this.http.post(url, payload);
  }

  uploadAudio(audioFile: File) {
    const url = `${environment.serviceUrl}/api/nlp/`;
    const formData = new FormData();
    formData.append('file', audioFile, audioFile.name);

    // ✅ Debug: ตรวจสอบว่า FormData มีค่าอะไรบ้าง
    for (let pair of formData.entries()) {
        console.log("🔹 FormData:", pair[0], pair[1]);  
    }

    return this.http.post(url, formData, {
        headers: { 'Accept': 'application/json' },
        withCredentials: true,
        observe: 'response'
    });
  }
}
