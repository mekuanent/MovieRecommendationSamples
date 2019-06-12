import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import {FormControl} from '@angular/forms';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {

  constructor(private httpClient: HttpClient) { 

    
  }

  topRated : any[]

  ngOnInit() {
    let that = this
    this.httpClient.get('http://localhost:5000/top', {}).subscribe(
      (data : any) => {
        that.topRated = data.results as any[]
      })

  }

  currentMovie = null
  similarMovies : any[]

  movieClicked(movie){

    let that = this
    this.httpClient.get('http://localhost:5000/recommendation/' + movie.name, {}).subscribe(
      (data : any) => {
        that.similarMovies = data.results as any[]
        that.currentMovie = movie
      })

  }

  currentUser = null
  myControl = new FormControl();
  options: string[] = ['13', '152', '198'];
  userId = null
  forme : any[]
  logIn(){
    let that = this
    this.httpClient.get('http://localhost:5000/for_me/' + this.userId, {}).subscribe(
      (data : any) => {
        that.forme = data.results as any[]
        that.currentUser = that.userId
      })
  }
}
