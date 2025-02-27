import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment.development';
import { map } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ProductService {

  private url = `${environment.serviceUrl}/api/menu`
  constructor(private http: HttpClient) { }

  getAllMenus(){
    let getUrl = `${this.url}`
    return this.http.get<any>(getUrl)
  }
}
