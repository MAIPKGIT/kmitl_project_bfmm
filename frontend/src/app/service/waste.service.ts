import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment.development';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class WasteService {

  constructor(private http: HttpClient) { }

  getAllWaste() {
    let getUrl = `${environment.serviceUrl}/api/waste/`;
    return this.http.get<any>(getUrl);
  }

  getWasteByDate(date: string) {
    let getUrl = `${environment.serviceUrl}/api/waste/date/${date}`;
    return this.http.get<any>(getUrl);
  }
}
