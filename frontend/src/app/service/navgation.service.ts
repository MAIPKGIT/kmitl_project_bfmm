import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment.development';

@Injectable({
  providedIn: 'root'
})
export class NavgationService {

  private url = `${environment.serviceUrl}/api/menutype/`
  constructor(private http: HttpClient) { }

  getAllMenuTypes(){
    let getUrl = `${this.url}`
    return this.http.get<any>(getUrl)
  }
  
}
