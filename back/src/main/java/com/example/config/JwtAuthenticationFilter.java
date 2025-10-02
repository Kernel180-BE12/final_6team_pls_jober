package com.example.config;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.lang.NonNull;
import lombok.RequiredArgsConstructor;
import com.example.service.TokenService;
import com.example.entity.Account;
import com.example.repository.AccountRepository;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.Collections;

@Component
@RequiredArgsConstructor
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtTokenProvider jwtTokenProvider;
    private final TokenService tokenService;
    private final AccountRepository accountRepository;

    @Override
    protected void doFilterInternal(@NonNull HttpServletRequest request, @NonNull HttpServletResponse response, 
                                  @NonNull FilterChain filterChain) throws ServletException, IOException {
        
        String requestURI = request.getRequestURI();
        String token = extractTokenFromRequest(request);
        
        // 템플릿 저장 요청에 대한 상세 로깅
        logTemplateSaveRequest(requestURI, token);
        
        // 토큰이 없거나 유효하지 않으면 인증 실패
        if (token == null || !jwtTokenProvider.validateToken(token)) {
            logAuthenticationFailure(requestURI, token == null ? "토큰이 없음" : "토큰 유효성 검사 실패");
            filterChain.doFilter(request, response);
            return;
        }
        
        // Access Token만 허용
        String tokenType = jwtTokenProvider.getTokenType(token);
        if (!"access".equals(tokenType)) {
            logAuthenticationFailure(requestURI, "토큰 타입이 access가 아님: " + tokenType);
            filterChain.doFilter(request, response);
            return;
        }
        
        // 블랙리스트 확인
        if (tokenService.isTokenBlacklisted(token)) {
            logAuthenticationFailure(requestURI, "토큰이 블랙리스트에 있음");
            filterChain.doFilter(request, response);
            return;
        }
        
        // JWT에서 accountId 추출
        Long accountId = jwtTokenProvider.getAccountId(token);
        if (accountId == null) {
            logAuthenticationFailure(requestURI, "accountId가 null");
            filterChain.doFilter(request, response);
            return;
        }
        
        // DB에서 실제 Account 엔티티 조회 (상태 확인)
        Account account = accountRepository.findById(accountId).orElse(null);
        if (account == null) {
            logAuthenticationFailure(requestURI, "계정을 찾을 수 없음 - ID: " + accountId);
            filterChain.doFilter(request, response);
            return;
        }
        
        if (!"ACTIVE".equals(account.getStatus())) {
            logAuthenticationFailure(requestURI, "계정 상태: " + account.getStatus() + " (ACTIVE가 아님)");
            filterChain.doFilter(request, response);
            return;
        }
        
        // 인증 성공 - Account 엔티티를 SecurityContext에 설정
        UsernamePasswordAuthenticationToken auth = new UsernamePasswordAuthenticationToken(
            account, // principal을 Account 엔티티로 설정
            null,
            Collections.singletonList(new SimpleGrantedAuthority(account.getRole()))
        );
        SecurityContextHolder.getContext().setAuthentication(auth);
        
        // 템플릿 저장 요청에 대한 성공 로깅
        if (requestURI.contains("/template/save")) {
            System.out.println("인증 성공 - 사용자 ID: " + accountId + ", 상태: " + account.getStatus());
        }
        
        filterChain.doFilter(request, response);
    }

    private String extractTokenFromRequest(HttpServletRequest request) {
        String bearerToken = request.getHeader("Authorization");
        if (bearerToken != null && bearerToken.startsWith("Bearer ")) {
            return bearerToken.substring(7);
        }
        return null;
    }
    
    private void logTemplateSaveRequest(String requestURI, String token) {
        if (requestURI.contains("/template/save")) {
            System.out.println("=== JWT 인증 필터 - 템플릿 저장 요청 ===");
            System.out.println("요청 URI: " + requestURI);
            System.out.println("토큰 존재 여부: " + (token != null));
            if (token != null) {
                System.out.println("토큰 길이: " + token.length());
                System.out.println("토큰 앞 20자: " + token.substring(0, Math.min(20, token.length())));
            }
        }
    }
    
    private void logAuthenticationFailure(String requestURI, String reason) {
        if (requestURI.contains("/template/save")) {
            System.out.println("인증 실패 - " + reason);
        }
    }
}
