package com.example.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HomeController {

    @GetMapping("/")
    public String home() {
        return "Final Project Backend is running!";
    }

    @GetMapping("/health")
    public String health() {
        return "OK";
    }
}

